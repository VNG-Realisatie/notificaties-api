from json import dumps

from django.test import override_settings

from mock import patch
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from vng_api_common.conf.api import BASE_REST_FRAMEWORK
from vng_api_common.tests import JWTScopesMixin, get_operation_url

from notifications.datamodel.tests.factories import (
    AbonnementFactory, FilterFactory, FilterGroupFactory, KanaalFactory
)

from ..channels import QueueChannel
from ..scopes import SCOPE_NOTIF_CHANGE_ALL, SCOPE_NOTIF_READ_ALL


@override_settings(
    LINK_FETCHER='vng_api_common.mocks.link_fetcher_200',
    ZDS_CLIENT_CLASS='vng_api_common.mocks.MockClient'
)
class NotificatieTests(JWTScopesMixin, APITestCase):

    scopes = [
        SCOPE_NOTIF_CHANGE_ALL,
        SCOPE_NOTIF_READ_ALL,
    ]

    @patch.object(QueueChannel, 'send')
    def test_notificatie_send_queue(self, mock_queue):
        """
        test /notificatie POST:
        check if message was send to RabbitMQ

        """
        kanaal_zaken = KanaalFactory.create(naam='zaken')
        notificatie_url = reverse('notificaties-list',
                                  kwargs={'version': BASE_REST_FRAMEWORK['DEFAULT_VERSION']})
        request_data = {
            "kanaal": "zaken",
            "bronUrl": "https://ref.tst.vng.cloud/zrc/api/v1/zaken/d7a22",
            "resource": "status",
            "resourceUrl": "https://ref.tst.vng.cloud/zrc/api/v1/statussen/d7a22/721c9",
            "actie": "create",
            "aanmaakDatum": "2018-01-01T17:00:00Z",
            "kenmerken": [
                {"bron": "082096752011"},
                {"zaaktype": "example.com/api/v1/zaaktypen/5aa5c"},
                {"vertrouwelijkeidaanduiding": "openbaar"}
            ]
        }

        response = self.client.post(notificatie_url, request_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        data = response.json()

        mock_queue.assert_called_with(dumps(data))

    @patch('notifications.api.serializers.requests.post')
    @patch.object(QueueChannel, 'send')
    def test_notificatie_send_abonnement(self, mock_queue, mock_post):
        """
        test /notificatie POST:
        check if message was send to subscribers callbackUrls

        """
        kanaal = KanaalFactory.create(naam='zaken')
        abon = AbonnementFactory.create(callback_url='https://example.com/callback')
        filter_group = FilterGroupFactory.create(kanaal=kanaal, abonnement=abon)
        filter = FilterFactory.create(filter_group=filter_group, key='bron', value='082096752011')
        notificatie_url = reverse('notificaties-list',
                                  kwargs={'version': BASE_REST_FRAMEWORK['DEFAULT_VERSION']})
        request_data = {
            "kanaal": "zaken",
            "bronUrl": "https://ref.tst.vng.cloud/zrc/api/v1/zaken/d7a22",
            "resource": "status",
            "resourceUrl": "https://ref.tst.vng.cloud/zrc/api/v1/statussen/d7a22/721c9",
            "actie": "create",
            "aanmaakDatum": "2018-01-01T17:00:00Z",
            "kenmerken": [
                {"bron": "082096752011"},
                {"zaaktype": "example.com/api/v1/zaaktypen/5aa5c"},
                {"vertrouwelijkeidaanduiding": "openbaar"}
            ]
        }

        response = self.client.post(notificatie_url, request_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        mock_post.assert_called_with(
            'https://example.com/callback',
            data=response.data,
            headers={'Authorization': abon.auth}
        )
