#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from apartment_hunt import geoutils
from apartment_hunt.providers.base import BaseListingProvider, BaseListing
from dateutil import parser
from requests_oauthlib import OAuth1
import json
import re
import requests


class ImmobilienScoutListing(BaseListing):

    _non_decimal_chars = re.compile(r'[^(\d\.,).]+')

    def __init__(self, json_data, **kwargs):
        """
        Create the listing with data from a call to the unofficial search API
        """
        self.id = json_data['id']
        self.room_count = float(self._get_attribute(json_data, 'Zimmer').replace(',', '.'))  # 1,5 is a possible value
        self.address = json_data['address']
        self.url = 'http://www.immobilienscout24.de/expose/{id}'.format(id=self.id)

        # Get the full size pictures' URLs without hitting an API call
        self.pictures = []
        for picture in json_data.get('pictureUrls', []):
            truncate_at = picture.find('/ORIG/') + len('/ORIG/')
            if truncate_at > -1:
                picture = picture[0:truncate_at]
            self.pictures.append(picture)

        # Formatted as 1.084,98 €
        self.base_rent = float(self._non_decimal_chars.sub('', self._get_attribute(json_data, 'Kaltmiete')).replace('.', '').replace(',', '.'))

        # Formatted as 84,71 m²
        self.size = float(self._non_decimal_chars.sub('', self._get_attribute(json_data, u'Wohnfläche')).replace('.', '').replace(',', '.'))

        self.geolocation = None
        if json_data.get('latitude') and json_data.get('longitude'):
            self.geolocation = {
                'lat': json_data.get('latitude'),
                'lng': json_data.get('longitude'),
            }

    def fetch_details(self, **kwargs):
        """
        Extend the listing with data from the expose API
        """
        client_key = kwargs.pop('immobilienscout_api_key')
        client_secret = kwargs.pop('immobilienscout_api_secret')

        api = ImmobilienScoutExposeApi(client_key=client_key, client_secret=client_secret)
        json_results = api.get_listing_details(self.id)
        self.floor = json_results['realEstate'].get('floor', None)
        self.floor_count = json_results['realEstate'].get('numberOfFloors', None)

        self.base_rent = json_results['realEstate']['baseRent']
        self.total_rent = json_results['realEstate'].get('totalRent', self.base_rent)

        self.available_from = json_results['realEstate'].get('freeFrom')

        date_published = json_results['@publishDate'][0:-3] + json_results['@publishDate'][-2:]
        self.date_published = parser.parse(date_published)

    def _get_attribute(self, json_data, attribute_name):
        return [a['value'] for a in json_data['attributes'] if a['title'] == attribute_name][0]


class ImmobilienScoutProvider(BaseListingProvider):
    search_url = 'http://www.immobilienscout24.de/Suche/controller/asyncResults.go?searchUrl=/Suche/S-2/P-{page}/Wohnung-Miete/{city}/{city}/-/{min_rooms}-{max_rooms}/{min_size}-/EURO--{max_rent}/-/128,117,127,118,6,7,40,8,3,113'

    def __init__(self, *args, **kwargs):
        self.client_key = kwargs.pop('immobilienscout_api_key')
        self.client_secret = kwargs.pop('immobilienscout_api_secret')
        self.google_api_key = kwargs.pop('google_api_key')
        self.immobilienscout_city = kwargs.pop('immobilienscout_city')
        super(ImmobilienScoutProvider, self).__init__(*args, **kwargs)

    def _get_results_page(self, page):
        url = self.search_url.format(
            page=page,
            max_rent=str(self.max_rent).replace('.', ','),
            min_size=str(self.min_size).replace('.', ','),
            min_rooms=str(self.min_room_count).replace('.', ','),
            max_rooms=str(self.max_room_count).replace('.', ','),
            city=self.immobilienscout_city,
        )
        response = requests.get(url=url, params={})
        response_json = json.loads(response.text)
        results = [ImmobilienScoutListing(r) for r in response_json['searchResult']['results']]

        return results

    def prefiltered_results(self, results):
        """
        Filter what can be filtered with the incomplete listings to reduce the number
        of API calls
        """
        def is_relevant(result):
            return (
                result.base_rent <= self.max_rent
                and result.room_count >= self.min_room_count
                and result.room_count <= self.max_room_count
                and (
                    not result.geolocation
                    or (result.geolocation and geoutils.direct_distance(self.near, result.geolocation) <= self.max_distance)
                )
                and result.size >= self.min_size
            )

        return filter(is_relevant, results)

    def extended_results(self, results):
        """
        Gets additional information about a listing.
        """
        valid_results = []

        for result in results:
            result.fetch_details(immobilienscout_api_key=self.client_key, immobilienscout_api_secret=self.client_secret)

            # Once we hit a result that's older than self.published_after, we stop
            # fetching details, since all subsequent results are too old and we'd
            # be wasting API calls.
            if self.published_after and result.date_published < self.published_after:
                break

            commute_info = geoutils.commute_information(self.near, result.geolocation or result.address, google_api_key=self.google_api_key)
            if commute_info:
                result.commute_summary = commute_info.get('summary')
                result.commute_duration = commute_info.get('duration') / 60 if commute_info.get('duration') else None
            valid_results.append(result)

        return valid_results

    def get_results(self):
        results = []
        page = 1
        for page in range(1, 10):
            results += self._get_results_page(page)

        results = self.prefiltered_results(results)
        results = self.extended_results(results)

        return self.filtered_results(results)


class ImmobilienScoutExposeApi(object):
    def __init__(self, **kwargs):
        self.client_key = kwargs.pop('client_key')
        self.client_secret = kwargs.pop('client_secret')

    def oauth_request(self, url):
        oauth = OAuth1(self.client_key, client_secret=self.client_secret)
        return requests.get(url, auth=oauth, headers={'Accept': 'application/json'})

    def get_listing_details(self, id):
        url = 'https://rest.immobilienscout24.de/restapi/api/search/v1.0/expose/{id}'.format(id=id)
        return json.loads(self.oauth_request(url).content)['expose.expose']
