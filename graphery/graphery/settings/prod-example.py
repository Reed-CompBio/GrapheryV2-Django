from .base import *

# use from django.core.management.utils import get_random_secret_key
# to generate a secretkey
SECRET_KEY = "twr*=4x$rd$tisv0ibq6*a-eur+0p4@%t+dwsz8!6_gj^yep*a"

DEBUG = False

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

CORS_ORIGIN_WHITELIST = ["https://graphery.reedcompbio.org"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "test",
        "USER": "graphery",
        "PASSWORD": "graphery",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}
