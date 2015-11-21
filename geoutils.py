from dateutil.tz import tzlocal
from dateutil.relativedelta import relativedelta
import requests
import json
import math
import datetime
import config


def direct_distance(coordinate1, coordinate2):
    """
    Bird's flight distance between two coordinates (in meters)
    """
    degrees_to_radians = math.pi / 180.0

    # phi = 90 - latitude
    phi1 = (90.0 - coordinate1['lat']) * degrees_to_radians
    phi2 = (90.0 - coordinate2['lat']) * degrees_to_radians

    # theta = longitude
    theta1 = coordinate1['lng'] * degrees_to_radians
    theta2 = coordinate2['lng'] * degrees_to_radians
    cos = (math.sin(phi1) * math.sin(phi2) * math.cos(theta1 - theta2) +
           math.cos(phi1) * math.cos(phi2))
    arc = math.acos(cos)

    return arc * 6.373


def commute_information(origin, destination):
    """
    Use the Google Directions API to find basic commute information.
    Calculates routes at 10AM in the current timezone
    """
    api_url = 'https://maps.googleapis.com/maps/api/directions/json?'

    if isinstance(origin, dict):
        origin = '{0},{1}'.format(origin['lat'], origin['lng'])
    if isinstance(destination, dict):
        destination = '{0},{1}'.format(destination['lat'], destination['lng'])

    params = {
        'origin': origin,
        'destination': destination,
        'mode': 'transit',
        'departure_time': (datetime.datetime.now(tzlocal()) + relativedelta(hour=10)).microsecond,  # At 10AM
        'transit_routing_preference': 'fewer_transfers',
        'key': config.GOOGLE_API_KEY,
    }
    response = requests.get(url=api_url, params=params)
    response_json = json.loads(response.text)

    if len(response_json['routes']) == 0:
        return None

    route = response_json['routes'][0]['legs'][0]

    # Build a list of train/bus routes to get to the destination
    transports_used = []
    for step in route['steps']:
        line = step.get('transit_details', {}).get('line', {}).get('short_name')
        if line:
            transports_used.append(line)

    # No lines, just walking
    if len(transports_used) == 0:
        transports_used.append('walk')

    return {
        'summary': transports_used,
        'duration': route['duration']['value'],
    }
