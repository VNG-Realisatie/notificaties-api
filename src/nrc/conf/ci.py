from .base import *  # noqa

#
# Standard Django settings.
#

DEBUG = False

ADMINS = ()

CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/stable/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["testserver.com"]

for logger in LOGGING["loggers"].values():
    logger.update(
        {
            "level": "CRITICAL",
            "handlers": [],
            "propagate": False,
        }
    )
LOGGING["loggers"][""] = {"level": "CRITICAL", "handlers": []}

#
# Custom settings
#

# Show active environment in admin.
ENVIRONMENT = "ci"

TEST_CALLBACK_AUTH = False
