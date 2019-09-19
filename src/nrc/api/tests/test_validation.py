from django.test import override_settings

import requests_mock
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import JWTAuthMixin, get_operation_url, get_validation_errors

from nrc.datamodel.tests.factories import KanaalFactory


class AbonnementenValidationTests(JWTAuthMixin, APITestCase):

    heeft_alle_autorisaties = True

    @override_settings(
        LINK_FETCHER="vng_api_common.mocks.link_fetcher_404",
        ZDS_CLIENT_CLASS="vng_api_common.mocks.MockClient",
    )
    def test_abonnementen_invalid_callback_url(self):
        KanaalFactory.create(
            naam="zaken", filters=["bron", "zaaktype", "vertrouwelijkheidaanduiding"]
        )
        KanaalFactory.create(naam="informatieobjecten", filters=[])
        abonnement_create_url = get_operation_url("abonnement_create")

        data = {
            "callbackUrl": "https://some-non-existent-url.com/",
            "auth": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImNsaWVudF9pZG"
            "VudGlmaWVyIjoienJjIn0.eyJpc3MiOiJ6cmMiLCJpYXQiOjE1NTI5OTM"
            "4MjcsInpkcyI6eyJzY29wZXMiOlsiemRzLnNjb3Blcy56YWtlbi5hYW5t"
            "YWtlbiJdLCJ6YWFrdHlwZXMiOlsiaHR0cDovL3p0Yy5ubC9hcGkvdjEve"
            "mFha3R5cGUvMTIzNCJdfX0.NHcWwoRYMuZ5IoUAWUs2lZFxLVLGhIDnU_"
            "LWTjyGCD4",
            "kanalen": [
                {
                    "naam": "zaken",
                    "filters": {
                        "bron": "082096752011",
                        "zaaktype": "example.com/api/v1/zaaktypen/5aa5c",
                        "vertrouwelijkheidaanduiding": "*",
                    },
                },
                {"naam": "informatieobjecten", "filters": {"bron": "082096752011"}},
            ],
        }

        with requests_mock.mock() as m:
            # Let callback url return 201 instead of required 204 when
            # sending a notification
            m.register_uri(
                "POST", "https://some-non-existent-url.com/", status_code=201
            )
            response = self.client.post(abonnement_create_url, data)

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.data
        )

        error = get_validation_errors(response, "nonFieldErrors")
        self.assertEqual(error["code"], "invalid-callback-url")

    @override_settings(
        LINK_FETCHER="vng_api_common.mocks.link_fetcher_404",
        ZDS_CLIENT_CLASS="vng_api_common.mocks.MockClient",
        TEST_CALLBACK_AUTH=True,
    )
    def test_abonnementen_callback_url_no_auth(self):
        KanaalFactory.create(
            naam="zaken", filters=["bron", "zaaktype", "vertrouwelijkheidaanduiding"]
        )
        KanaalFactory.create(naam="informatieobjecten", filters=[])
        abonnement_create_url = get_operation_url("abonnement_create")

        data = {
            "callbackUrl": "https://some-non-existent-url.com/",
            "auth": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImNsaWVudF9pZG"
            "VudGlmaWVyIjoienJjIn0.eyJpc3MiOiJ6cmMiLCJpYXQiOjE1NTI5OTM"
            "4MjcsInpkcyI6eyJzY29wZXMiOlsiemRzLnNjb3Blcy56YWtlbi5hYW5t"
            "YWtlbiJdLCJ6YWFrdHlwZXMiOlsiaHR0cDovL3p0Yy5ubC9hcGkvdjEve"
            "mFha3R5cGUvMTIzNCJdfX0.NHcWwoRYMuZ5IoUAWUs2lZFxLVLGhIDnU_"
            "LWTjyGCD4",
            "kanalen": [
                {
                    "naam": "zaken",
                    "filters": {
                        "bron": "082096752011",
                        "zaaktype": "example.com/api/v1/zaaktypen/5aa5c",
                        "vertrouwelijkheidaanduiding": "*",
                    },
                },
                {"naam": "informatieobjecten", "filters": {"bron": "082096752011"}},
            ],
        }

        with requests_mock.mock() as m:
            m.register_uri(
                "POST", "https://some-non-existent-url.com/", status_code=204
            )
            response = self.client.post(abonnement_create_url, data)

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.data
        )

        error = get_validation_errors(response, "callbackUrl")
        self.assertEqual(error["code"], "no-auth-on-callback-url")


class KanalenValidationTests(JWTAuthMixin, APITestCase):

    heeft_alle_autorisaties = True

    @override_settings(
        LINK_FETCHER="vng_api_common.mocks.link_fetcher_404",
        ZDS_CLIENT_CLASS="vng_api_common.mocks.MockClient",
    )
    def test_kanalen_invalid_documentatie_link_url(self):
        abonnement_create_url = get_operation_url("kanaal_create")

        data = {"naam": "testkanaal", "documentatieLink": "https://some-bad-url.com/"}

        response = self.client.post(abonnement_create_url, data)

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.data
        )

        error = get_validation_errors(response, "documentatieLink")
        self.assertEqual(error["code"], "bad-url")


class NotificatiesValidationTests(JWTAuthMixin, APITestCase):

    heeft_alle_autorisaties = True

    @freeze_time("2019-01-01T12:00:00Z")
    @override_settings(
        LINK_FETCHER="vng_api_common.mocks.link_fetcher_200",
        ZDS_CLIENT_CLASS="vng_api_common.mocks.MockClient",
    )
    def test_notificaties_aanmaakdatum_in_future_fails(self):
        KanaalFactory.create(naam="zaken")
        notificatie_url = get_operation_url("notificaties_create")
        data = {
            "kanaal": "zaken",
            "hoofdObject": "https://ref.tst.vng.cloud/zrc/api/v1/zaken/d7a22",
            "resource": "status",
            "resourceUrl": "https://ref.tst.vng.cloud/zrc/api/v1/statussen/d7a22/721c9",
            "actie": "create",
            "aanmaakdatum": "2019-01-01T13:00:00Z",
            "kenmerken": {
                "bron": "082096752011",
                "zaaktype": "example.com/api/v1/zaaktypen/5aa5c",
                "vertrouwelijkheidaanduiding": "openbaar",
            },
        }

        response = self.client.post(notificatie_url, data)

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.data
        )

        self.assertIn("aanmaakdatum", response.data)

        error = response.data["aanmaakdatum"][0]
        self.assertEqual(error.code, "future_not_allowed")
