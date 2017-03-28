# Apartment hunt tool

This module will fetch apartment listings from *providers* such as ImmobilienScout24 based on predefined criteria. Here's a simple code example:

```python
results = ImmobilienScoutProvider(near=near, city='Berlin', max_distance=8000, max_commute_duration=30, max_rent=900, top_floor_only=True).get_results()
```

## But why?

Most apartment listing websites make it really hard to see what really matters when apartment hunting. For instance, there's no way to say "I want an apartment that's less than 30 minutes from work", or "I only want to see apartments on the top floor".

Also, it can be quite hard to be the first to bid on an apartment in crazy markets like Berlin. It would be trivial to send matching listings directly to your phone with [Pushover](https://pushover.net).

## How it works

### Setting up the project

This repository holds a Python module that can be installed with pip (`pip install git+https://github.com/nicbou/apartment-hunt.git@master`).

### ListingProviders

ListingProviders extend `BaseListingProvider` and return instances of `BaseListing`. The provider's role is to take a standard list of filters such as `max_rent`, `max_commute_duration` etc. and only return matching listings from an arbitrary source.

Take a look at `BaseListingProvider` under `apartment_hunt/providers/base.py`, then `apartment_hunt/providers/immobilienscout.py` to get an idea of how providers work.

### Utility classes

The `geoutils` module provides some useful functions to calculate the distance between geographical coordinates.

```python
from apartment_hunt.geoutils import direct_distance

coordinate1 = {lat: ..., lon: ...}
coordinate2 = {lat: ..., lon: ...}

print(direct_distance(coordinate1, coordinate2))  # Distance in meters
print(commute_information(coordinate1, coordinate2, google_api_key=...))  # {'commute_summary':['U6', 'S5', 'M10'], 'commute_duration': 30}
```

### Getting results

Here is how to use the ImmobilienScoutProvider. Aside from the `immobilienscout_*` parameters, all other parameters are meant to be supported by all ListingProviders.

```python
# Our search criteria, passed as kwargs to our providers
params = {
    'date_published': a_datetime_object,
    'google_api_key': ...,
    'near': {'lat': ..., 'lng': ...},  # Within x minutes or kilometers from this point
    'max_commute_duration': 30,  # 30 minutes from work using public transit
    'max_distance': 12000,  # Less than 12km from work. Saves some Google Directions API calls
    'max_rent': 900,  # 900 euros or less
    'top_floor_only': True,  # Only return top floor apartments (and those with undefined top floor)
    'immobilienscout_city': 'Berlin',
    'immobilienscout_api_secret': ...,
    'immobilienscout_api_key': ...,
}

results = ImmobilienScoutProvider(**params).get_results()  # Returns a list of ImmobilienScoutListing items
```
