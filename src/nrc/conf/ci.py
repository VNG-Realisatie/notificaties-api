import os

from .includes.base import *  # noqa

os.environ.setdefault("IS_HTTPS", "no")


#
# Standard Django settings.
#

ADMINS = ()

CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    # https://github.com/jazzband/django-axes/blob/master/docs/configuration.rst#cache-problems
    "axes": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"},
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/stable/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["testserver.com"]

for logger in LOGGING["loggers"].values():
    logger.update(
        {"level": "CRITICAL", "handlers": [], "propagate": False,}
    )
LOGGING["loggers"][""] = {"level": "CRITICAL", "handlers": []}

#
# Custom settings
#

# Show active environment in admin.
ENVIRONMENT = "ci"

TEST_CALLBACK_AUTH = False
