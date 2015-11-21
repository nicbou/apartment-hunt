#Apartment hunt tool

This framework will fetch apartment listings from *providers* such as ImmobilienScout24 based on predefined criteria. Here's a simple code example:

```python
results = ImmobilienScoutProvider(near=near, city='Berlin', max_distance=8000, max_commute_duration=30, max_rent=900, top_floor_only=True).get_results()
```

##But why?

Most apartment listing websites make it really hard to see what really matters when apartment hunting. For instance, there's no way to say "I want an apartment that's less than 30 minutes from work", or "I only want to see apartments on the top floor".

Also, it can be quite hard to be the first to bid on an apartment in crazy markets like Berlin. It would be trivial to send matching listings directly to your phone with [Pushover](https://pushover.net).

##How it works

###Running the project

Pull this repository, then run `pip install -r requirements.txt`, and update `config.py.example` with your own API keys before renaming it to `config.py`.

This project is mostly a set of utility classes. `run.py` is a very simple script that makes use of them. You can run it directly, or implement your own application around the framework.

###ListingProviders

ListingProviders extend `BaseListingProvider` and return instances of `BaseListing`. The provider's role is to take a standard list of filters such as `max_rent`, `max_commute_duration` etc. and only return matching listings from an arbitrary source.

Take a look at `BaseListingProvider` under `providers/base.py`, then `providers/immobilienscout.py` to get an idea of how providers work.

###Getting results

Once you have your providers configured, you can request results with the following syntax:

```python
results = ImmobilienScoutProvider(near=near, city='Berlin', max_distance=8000, max_commute_duration=30, max_rent=900).get_results()
```