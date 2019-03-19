from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import JWTScopesMixin, get_operation_url

from notifications.datamodel.models import (
    Abonnement, Filter, FilterGroup, Kanaal
)
from notifications.datamodel.tests.factories import (
    AbonnementFactory, KanaalFactory
)

from ..scopes import SCOPE_NOTIFICATIES_CONSUMEREN


@override_settings(
    LINK_FETCHER='vng_api_common.mocks.link_fetcher_200',
    ZDS_CLIENT_CLASS='vng_api_common.mocks.MockClient'
)
class AbonnementenTests(JWTScopesMixin, APITestCase):

    scopes = [
        SCOPE_NOTIFICATIES_CONSUMEREN,
    ]

    def test_abonnementen_create(self):
        """
        test /abonnementen POST:
        create abonnement with nested kanalen and nested filters via POST request
        check if data were parsed to models correctly
        """

        kanaal_zaken = KanaalFactory.create(naam='zaken')
        kanaal_informatieobjecten = KanaalFactory.create(naam='informatieobjecten')
        abonnement_create_url = get_operation_url('abonnement_create')
        data = {
            "callbackUrl": "https://ref.tst.vng.cloud/zrc/api/v1/callbacks",
            "auth": "Bearer aef34gh",
            "kanalen": [{
                "naam": "zaken",
                "filters": [
                    {"bron": "082096752011"},
                    {"zaaktype": "example.com/api/v1/zaaktypen/5aa5c"},
                    {"vertrouwelijkheidaanduiding": "*"}
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
        filter_group = abon.filter_groups.all().order_by('id')[0]
        filters = filter_group.filters.all().order_by('id')
        filters_str = [str(f) for f in filters]

        self.assertEqual(Abonnement.objects.count(), 1)
        self.assertEqual(Kanaal.objects.count(), 2)
        self.assertEqual(FilterGroup.objects.count(), 2)
        self.assertEqual(Filter.objects.count(), 4)
        self.assertEqual(
            abon.callback_url,
            "https://ref.tst.vng.cloud/zrc/api/v1/callbacks")
        self.assertEqual(
            filter_group.kanaal.naam,
            'zaken')
        self.assertListEqual(
            filters_str,
            ["bron: 082096752011", "zaaktype: example.com/api/v1/zaaktypen/5aa5c", "vertrouwelijkheidaanduiding: *"])

    def test_abonnementen_create_nonexistent_kanaal(self):
        """
        test /abonnementen POST:
        attempt to create abonnement with nested nonexistent kanalen
        check if response contents status 400
        """
        abonnement_create_url = get_operation_url('abonnement_create')
        data = {
            "callbackUrl": "https://ref.tst.vng.cloud/zrc/api/v1/callbacks",
            "auth": "Bearer aef34gh",
            "kanalen": [{
                "naam": "zaken",
                "filters": [
                    {"bron": "082096752011"},
                    {"zaaktype": "example.com/api/v1/zaaktypen/5aa5c"},
                    {"vertrouwelijkheidaanduiding": "*"}
                ]
            }, {
                "naam": "informatieobjecten",
                "filters": [
                    {"bron": "082096752011"}
                ]
            }]
        }

        response = self.client.post(abonnement_create_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

    def test_abonnement_update_kanalen(self):
        """
        test /abonnementen PUT:
        update existent abonnement which has its kanaal via request which contains another kanaal
        check if relation between abonnement and previous kanalen was removed
        check if relation between abonnement and new kanaal was created
        """
        abonnement = AbonnementFactory.create()
        kanaal_foo = KanaalFactory.create(naam='foo')
        kanaal_zaken = KanaalFactory.create(naam='zaken')
        abonnement.kanalen.add(kanaal_foo)
        data = {
            "callbackUrl": "https://other.url/callbacks",
            "kanalen": [{
                "naam": "zaken",
                "filters": [
                    {"bron": "082096752011"},
                    {"zaaktype": "example.com/api/v1/zaaktypen/5aa5c"},
                    {"vertrouwelijkheidaanduiding": "*"}
                ]
            }]
        }
        abonnement_update_url = get_operation_url('abonnement_update', uuid=abonnement.uuid)

        response = self.client.put(abonnement_update_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        data = response.json()
        kanalen = abonnement.kanalen

        self.assertEqual(len(kanalen), 1)
        self.assertEqual(kanalen.pop().naam, 'zaken')
