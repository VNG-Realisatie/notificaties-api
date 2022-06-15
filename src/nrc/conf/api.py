import os

from vng_api_common.conf.api import *  # noqa - imports white-listed

API_VERSION = "2.0.0-alpha8"

REST_FRAMEWORK = BASE_REST_FRAMEWORK.copy()
REST_FRAMEWORK.update(
    {"DEFAULT_PERMISSION_CLASSES": ("vng_api_common.permissions.AuthScopesRequired",)}
)

SECURITY_DEFINITION_NAME = "JWT-Claims"

SWAGGER_SETTINGS = BASE_SWAGGER_SETTINGS.copy()
SWAGGER_SETTINGS.update(
    {
        "DEFAULT_INFO": "nrc.api.schema.info",
        "SECURITY_DEFINITIONS": {
            SECURITY_DEFINITION_NAME: {
                # OAS 3.0
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                # not official...
                # 'scopes': {},  # TODO: set up registry that's filled in later...
                # Swagger 2.0
                # 'name': 'Authorization',
                # 'in': 'header'
                # 'type': 'apiKey',
            }
        },
    }
)

GEMMA_URL_INFORMATIEMODEL_VERSIE = "1.0"

TEST_CALLBACK_AUTH = True

SELF_REPO = "VNG-Realisatie/notificaties-api"
SELF_BRANCH = os.getenv("SELF_BRANCH") or API_VERSION
GITHUB_API_SPEC = f"https://raw.githubusercontent.com/{SELF_REPO}/{SELF_BRANCH}/src/openapi.yaml"  # noqa
