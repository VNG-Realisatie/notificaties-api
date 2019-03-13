from django.test import override_settings, tag

from rest_framework import status
from rest_framework.test import APITestCase
from zds_schema.tests import JWTScopesMixin, get_operation_url

from notifications.datamodel.models import Abonnement

from ..scopes import (
    SCOPE_SUB_CHANGE_ALL, SCOPE_SUB_READ_ALL
)


@override_settings(
    LINK_FETCHER='zds_schema.mocks.link_fetcher_200',
    ZDS_CLIENT_CLASS='zds_schema.mocks.MockClient'
)
class AbonnementenTests(JWTScopesMixin, APITestCase):

    scopes = [
        SCOPE_SUB_READ_ALL,
        SCOPE_SUB_CHANGE_ALL,
    ]

    def test_abonnementen_create(self):
        abonnement_create_url = get_operation_url('abonnement_create')
        data = {
            "callbackUrl": "https://ref.tst.vng.cloud/zrc/api/v1/callbacks",
            "auth": "Bearer aef34gh",
            "kanalen": [{
                "naam": "zaken",
                "filters": [
                    {"bron": "082096752011"},
                    {"zaaktype": "example.com/api/v1/zaaktypen/5aa5c"},
                    {"vertrouwelijkeidaanduiding": "*"}
                ]
            }, {
                "naam": "informatieobjecten",
                "filters": [
                    {"bron": "082096752011"}
                ]
            }]
        }

        response = self.client.post(abonnement_create_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        # check parsing to models
        data = response.json()

        abon = Abonnement.objects.get()
        kanaal = abon.kanalen.all().order_by('id')[0]
        filters = kanaal.filters.all().order_by('id')
        filters_str = [str(f) for f in filters]

        self.assertEqual(
            abon.callback_url,
            "https://ref.tst.vng.cloud/zrc/api/v1/callbacks")
        self.assertEqual(
            kanaal.naam,
            'zaken')
        self.assertListEqual(
            filters_str,
            ["bron: 082096752011", "zaaktype: example.com/api/v1/zaaktypen/5aa5c", "vertrouwelijkeidaanduiding: *"])

