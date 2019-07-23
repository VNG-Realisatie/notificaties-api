from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import (
    JWTAuthMixin, get_operation_url, get_validation_errors
)

from nrc.datamodel.tests.factories import KanaalFactory


class AbonnementenValidationTests(JWTAuthMixin, APITestCase):

    heeft_alle_autorisaties = True

    @override_settings(
        LINK_FETCHER='vng_api_common.mocks.link_fetcher_404',
        ZDS_CLIENT_CLASS='vng_api_common.mocks.MockClient'
    )
    def test_abonnementen_invalid_callback_url(self):
        KanaalFactory.create(naam='zaken', filters=['bron', 'zaaktype', 'vertrouwelijkheidaanduiding'])
        KanaalFactory.create(naam='informatieobjecten', filters=[])
        abonnement_create_url = get_operation_url('abonnement_create')

        data = {
            "callbackUrl": "https://some-non-existent-url.com/",
            "auth": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImNsaWVudF9pZG"
                    "VudGlmaWVyIjoienJjIn0.eyJpc3MiOiJ6cmMiLCJpYXQiOjE1NTI5OTM"
                    "4MjcsInpkcyI6eyJzY29wZXMiOlsiemRzLnNjb3Blcy56YWtlbi5hYW5t"
                    "YWtlbiJdLCJ6YWFrdHlwZXMiOlsiaHR0cDovL3p0Yy5ubC9hcGkvdjEve"
                    "mFha3R5cGUvMTIzNCJdfX0.NHcWwoRYMuZ5IoUAWUs2lZFxLVLGhIDnU_"
                    "LWTjyGCD4",
            "kanalen": [{
                "naam": "zaken",
                "filters": {
                    "bron": "082096752011",
                    "zaaktype": "example.com/api/v1/zaaktypen/5aa5c",
                    "vertrouwelijkheidaanduiding": "*"
                }
            }, {
                "naam": "informatieobjecten",
                "filters": {
                    "bron": "082096752011"
                }
            }]
        }

        response = self.client.post(abonnement_create_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

        error = get_validation_errors(response, 'callbackUrl')
        self.assertEqual(error['code'], 'bad-url')


class KanalenValidationTests(JWTAuthMixin, APITestCase):

    heeft_alle_autorisaties = True

    @override_settings(
        LINK_FETCHER='vng_api_common.mocks.link_fetcher_404',
        ZDS_CLIENT_CLASS='vng_api_common.mocks.MockClient'
    )
    def test_kanalen_invalid_documentatie_link_url(self):
        abonnement_create_url = get_operation_url('kanaal_create')

        data = {
            'naam': 'testkanaal',
            'documentatieLink': 'https://some-bad-url.com/'
        }

        response = self.client.post(abonnement_create_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

        error = get_validation_errors(response, 'documentatieLink')
        self.assertEqual(error['code'], 'bad-url')
