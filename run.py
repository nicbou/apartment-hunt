#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from providers.immobilienscout import ImmobilienScoutProvider

near = {  # Work
    'lat': 52.5309272,
    'lng': 13.382965
}

results = ImmobilienScoutProvider(near=near, city='Berlin', max_distance=8000, max_commute_duration=30, max_rent=900).get_results()

for result in results[0:10]:
    print(result)