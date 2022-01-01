from .base import *

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

CORS_ORIGIN_WHITELIST = ["http://localhost:8080", "http://localhost:8088"]

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
