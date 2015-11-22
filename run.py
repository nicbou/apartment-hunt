#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from providers.immobilienscout import ImmobilienScoutProvider
from dateutil.tz import tzlocal
import datetime
import shelve


# We use shelve to persist a couple of variables
db = shelve.open('persistence.db', writeback=True)

# Our search criteria, passed as kwargs to our providers
params = {
    'near': {  # Find places close to work
        'lat': 52.5309272,
        'lng': 13.382965
    },
    'immobilienscout_city': 'Berlin',
    'max_commute_duration': 30,  # 30 minutes from work using public transit
    'max_distance': 12000,  # Less than 12km from work. Saves some Google Directions API calls
    'max_rent': 900,  # 900 euros or less
    'posted_after': db.get('last_fetched'),
    'top_floor_only': True,
}

# This is how a search is performed
results = ImmobilienScoutProvider(**params).get_results()

# All results have a nice string representation defined in BaseListing
for result in results:
    print(result)

# Save the latest element
db['last_fetched'] = datetime.datetime.now(tzlocal())
db['immobilienscout_posted_after_id'] = results[0].id

db.sync()
db.close()
