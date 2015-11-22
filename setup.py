from distutils.core import setup

setup(
    name='apartment-hunt',
    version='1.0',
    description='Apartment listing fetcher',
    author='Nicolas Bouliane',
    author_email='contact@nicolasbouliane.com',
    url='http://github.com/nicbou/apartment-hunt',
    install_requires=['requests', 'requests_oauthlib', 'python-dateutil'],
    packages=['apartment_hunt', 'apartment_hunt.providers'],
)
