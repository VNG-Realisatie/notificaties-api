from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase
from zds_schema.tests import JWTScopesMixin, get_operation_url

from notifications.datamodel.models import Abonnement, Kanaal, Filter
from notifications.datamodel.tests.factories import AbonnementFactory, KanaalFactory

from ..scopes import SCOPE_NOTIF_CHANGE_ALL, SCOPE_NOTIF_READ_ALL


@override_settings(
    LINK_FETCHER='zds_schema.mocks.link_fetcher_200',
    ZDS_CLIENT_CLASS='zds_schema.mocks.MockClient'
)
class KanalenTests(JWTScopesMixin, APITestCase):

    scopes = [
        SCOPE_NOTIF_CHANGE_ALL,
        SCOPE_NOTIF_READ_ALL,
    ]

    def test_kanaal_create(self):
        """
        test /kanaal POST:
        create kanaal via POST request
        check if data were parsed to models correctly
        """
        kanaal_create_url = get_operation_url('kanaal_create')
        data = {
                "naam": "zaken",
                "documentatie_link": 'https://example.com/doc'
        }

        response = self.client.post(kanaal_create_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        # check parsing to model
        data = response.json()
        kanaal = Kanaal.objects.get()
        self.assertEqual(kanaal.naam, 'zaken')

    def test_kanaal_create_nonunique (self):
        """
        test /kanaal POST:
        attempt to create kanaal with the same name as an existent kanaal
        check if response contents status 400
        """
        kanaal = Kanaal.objects.create(naam='zaken')
        kanaal_create_url = get_operation_url('kanaal_create')
        data = {
            "naam": "zaken",
            "documentatie_link": 'https://example.com/doc'
        }

        response = self.client.post(kanaal_create_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

    def test_kanaal_update_delete(self):
        """
        test /kanaal PUT, DELETE:
        attempt to update and destroy kanaal via request
        check if response contents status 405
        """
        kanaal = Kanaal.objects.create(naam='zaken')
        kanaal_url = get_operation_url('kanaal_read', uuid=kanaal.uuid)
        data = {
            "documentatie_link": 'https://example.com/doc'
        }

        response_put = self.client.put(kanaal_url, data)

        self.assertEqual(response_put.status_code, status.HTTP_405_METHOD_NOT_ALLOWED, response_put.data)

        response_delete = self.client.delete(kanaal_url, data)

        self.assertEqual(response_delete.status_code, status.HTTP_405_METHOD_NOT_ALLOWED, response_delete.data)
