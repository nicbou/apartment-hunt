#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from dateutil.tz import tzlocal
import datetime
import geoutils


class BaseListingProvider(object):
    def __init__(self, **kwargs):
        self.set_filters(**kwargs)

    def set_filters(self, **kwargs):
        a_year_ago = datetime.datetime.now(tzlocal()) - datetime.timedelta(days=365)

        self.max_rent = kwargs.get('max_rent', 999999)
        self.min_room_count = kwargs.get('min_room_count', 0)
        self.max_room_count = kwargs.get('max_room_count', 999999)
        self.max_distance = kwargs.get('max_distance', 999999)
        self.max_commute_duration = kwargs.get('max_commute_duration', 999999)
        self.min_size = kwargs.get('min_size', 0)
        self.near = kwargs.get('near', {'lat': 0, 'lng': 0})
        self.published_after = kwargs.get('published_after') or a_year_ago
        self.top_floor_only = kwargs.get('top_floor_only', False)

    def get_results(self):
        return []

    def filtered_results(self, results):
        def is_relevant(result):
            return (
                result.base_rent <= self.max_rent
                and result.total_rent <= self.max_rent
                and result.room_count >= self.min_room_count
                and result.room_count <= self.max_room_count
                and (
                    not result.geolocation
                    or (result.geolocation and geoutils.direct_distance(self.near, result.geolocation) <= self.max_distance)
                )
                and (result.commute_duration <= self.max_commute_duration or not result.commute_duration or not self.max_commute_duration)
                and result.size >= self.min_size
                and result.date_published >= self.published_after
                and (result.floor == result.floor_count or not self.top_floor_only or not result.floor_count)
            )

        return filter(is_relevant, results)


class BaseListing(object):
    address = ''
    available_from = None
    floor = None
    floor_count = None
    geolocation = None
    id = None
    pictures = []
    rent = 0
    room_count = 0
    commute_duration = None
    url = None

    def __repr__(self):
        return "{rent:.0f}€, {room_count:.2g}br, {size}m², floor {floor}/{floor_count}, {commute_duration} minute commute. {url}".format(
            commute_duration=self.commute_duration or '?',
            floor=self.floor or '?',
            floor_count=self.floor_count or '?',
            rent=self.total_rent,
            room_count=self.room_count or '?',
            size=self.size,
            url=self.url or '',
        )
