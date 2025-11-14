import os

from vng_api_common.conf.api import *  # noqa - imports white-listed

API_VERSION = "2.0.0-alpha13"

DOCUMENTATION_INFO_MODULE = "nrc.api.schema"

REST_FRAMEWORK = BASE_REST_FRAMEWORK.copy()
REST_FRAMEWORK.update(
    {"DEFAULT_PERMISSION_CLASSES": ("vng_api_common.permissions.AuthScopesRequired",)}
)

SPECTACULAR_SETTINGS = BASE_SPECTACULAR_SETTINGS.copy()
SPECTACULAR_SETTINGS.update(
    {
        "SERVERS": [{"url": "https://notificaties-api.test.vng.cloud/api/v1"}],
    }
)
SPECTACULAR_EXTENSIONS = [
    "vng_api_common.extensions.fields.hyperlink_identity.HyperlinkedIdentityFieldExtension",
    "vng_api_common.extensions.fields.many_related.ManyRelatedFieldExtension",
    "vng_api_common.extensions.fields.read_only.ReadOnlyFieldExtension",
    "vng_api_common.extensions.filters.query.FilterExtension",
]
GEMMA_URL_INFORMATIEMODEL_VERSIE = "1.0"

TEST_CALLBACK_AUTH = True

SELF_REPO = "VNG-Realisatie/notificaties-api"
SELF_BRANCH = os.getenv("SELF_BRANCH") or API_VERSION
GITHUB_API_SPEC = f"https://raw.githubusercontent.com/{SELF_REPO}/{SELF_BRANCH}/src/openapi.yaml"  # noqa
