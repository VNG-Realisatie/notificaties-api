import json
from unittest import skip
from unittest.mock import patch

from django.core.serializers.json import DjangoJSONEncoder
from django.test import override_settings

import requests
import requests_mock
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from vng_api_common.conf.api import BASE_REST_FRAMEWORK
from vng_api_common.tests import JWTScopesMixin

from notifications.datamodel.models import Notificatie, NotificatieResponse
from notifications.datamodel.tests.factories import (
    AbonnementFactory, FilterFactory, FilterGroupFactory, KanaalFactory
)

from ..channels import QueueChannel
from ..scopes import SCOPE_NOTIFICATIES_PUBLICEREN


@patch.object(QueueChannel, 'send')
@override_settings(
    LINK_FETCHER='vng_api_common.mocks.link_fetcher_200',
    ZDS_CLIENT_CLASS='vng_api_common.mocks.MockClient'
)
class NotificatieTests(JWTScopesMixin, APITestCase):

    scopes = [
        SCOPE_NOTIFICATIES_PUBLICEREN,
    ]

    @skip('Sending to RabbitMQ is not currently supported')
    def test_notificatie_send_queue(self, mock_queue):
        """
        test /notificatie POST:
        check if message was send to RabbitMQ

        """
        KanaalFactory.create(naam='zaken')
        notificatie_url = reverse('notificaties-list',
                                  kwargs={'version': BASE_REST_FRAMEWORK['DEFAULT_VERSION']})
        request_data = {
            "kanaal": "zaken",
            "hoofdObject": "https://ref.tst.vng.cloud/zrc/api/v1/zaken/d7a22",
            "resource": "status",
            "resourceUrl": "https://ref.tst.vng.cloud/zrc/api/v1/statussen/d7a22/721c9",
            "actie": "create",
            "aanmaakdatum": "2018-01-01T17:00:00Z",
            "kenmerken": {
                "bron": "082096752011",
                "zaaktype": "example.com/api/v1/zaaktypen/5aa5c",
                "vertrouwelijkheidaanduiding": "openbaar"
            }
        }

        response = self.client.post(notificatie_url, request_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        mock_queue.assert_called_with(json.dumps(response.data, cls=DjangoJSONEncoder))

    def test_notificatie_send_abonnement(self, mock_queue):
        """
        test /notificatie POST:
        check if message was send to subscribers callbackUrls

        """
        kanaal = KanaalFactory.create(naam='zaken', filters=['bron', 'zaaktype', 'vertrouwelijkheidaanduiding'])
        abon = AbonnementFactory.create(callback_url='https://example.com/callback')
        filter_group = FilterGroupFactory.create(kanaal=kanaal, abonnement=abon)
        FilterFactory.create(filter_group=filter_group, key='bron', value='082096752011')
        notificatie_url = reverse('notificaties-list',
                                  kwargs={'version': BASE_REST_FRAMEWORK['DEFAULT_VERSION']})
        request_data = {
            "kanaal": "zaken",
            "hoofdObject": "https://ref.tst.vng.cloud/zrc/api/v1/zaken/d7a22",
            "resource": "status",
            "resourceUrl": "https://ref.tst.vng.cloud/zrc/api/v1/statussen/d7a22/721c9",
            "actie": "create",
            "aanmaakdatum": "2018-01-01T17:00:00Z",
            "kenmerken": {
                "bron": "082096752011",
                "zaaktype": "example.com/api/v1/zaaktypen/5aa5c",
                "vertrouwelijkheidaanduiding": "openbaar"
            }
        }

        with requests_mock.mock() as m:
            m.post(abon.callback_url)

            response = self.client.post(notificatie_url, request_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        self.assertEqual(m.last_request.url, 'https://example.com/callback')
        self.assertEqual(
            m.last_request.body,
            json.dumps(response.data, cls=DjangoJSONEncoder)
        )
        self.assertEqual(m.last_request.headers['Content-Type'], 'application/json')
        self.assertEqual(m.last_request.headers['Authorization'], abon.auth)

    def test_notificatie_log(self, mock_queue):
        """
        test /notificatie POST:
        check if message was send to subscribers callbackUrls

        """
        kanaal = KanaalFactory.create(naam='zaken', filters=['bron', 'zaaktype', 'vertrouwelijkheidaanduiding'])
        abon = AbonnementFactory.create(callback_url='https://example.com/callback')
        filter_group = FilterGroupFactory.create(kanaal=kanaal, abonnement=abon)
        FilterFactory.create(filter_group=filter_group, key='bron', value='082096752011')
        notificatie_url = reverse('notificaties-list',
                                  kwargs={'version': BASE_REST_FRAMEWORK['DEFAULT_VERSION']})
        request_data = {
            "kanaal": "zaken",
            "hoofdObject": "https://ref.tst.vng.cloud/zrc/api/v1/zaken/d7a22",
            "resource": "status",
            "resourceUrl": "https://ref.tst.vng.cloud/zrc/api/v1/statussen/d7a22/721c9",
            "actie": "create",
            "aanmaakdatum": "2018-01-01T17:00:00Z",
            "kenmerken": {
                "bron": "082096752011",
                "zaaktype": "example.com/api/v1/zaaktypen/5aa5c",
                "vertrouwelijkheidaanduiding": "openbaar"
            }
        }

        with requests_mock.mock() as m:
            m.post(abon.callback_url)

            response = self.client.post(notificatie_url, request_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(Notificatie.objects.count(), 1)

    def test_notificatie_send_abonnement_inconsistent_kenmerken(self, mock_queue):
        """
        test /notificatie POST:
        send message with kenmekren inconsistent with kanaal filters
        check if response contains status 400

        """
        kanaal = KanaalFactory.create(naam='zaken')
        abon = AbonnementFactory.create(callback_url='https://example.com/callback')
        filter_group = FilterGroupFactory.create(kanaal=kanaal, abonnement=abon)
        FilterFactory.create(filter_group=filter_group, key='bron', value='082096752011')
        notificatie_url = reverse('notificaties-list',
                                  kwargs={'version': BASE_REST_FRAMEWORK['DEFAULT_VERSION']})
        request_data = {
            "kanaal": "zaken",
            "hoofdObject": "https://ref.tst.vng.cloud/zrc/api/v1/zaken/d7a22",
            "resource": "status",
            "resourceUrl": "https://ref.tst.vng.cloud/zrc/api/v1/statussen/d7a22/721c9",
            "actie": "create",
            "aanmaakdatum": "2018-01-01T17:00:00Z",
            "kenmerken": {
                "bron": "082096752011",
                "zaaktype": "example.com/api/v1/zaaktypen/5aa5c",
                "vertrouwelijkheidaanduiding": "openbaar"
            }
        }

        with requests_mock.mock() as m:
            m.post(abon.callback_url)

            response = self.client.post(notificatie_url, request_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        validation_error = response.data['kenmerken'][0]
        self.assertEqual(validation_error.code, 'kenmerken_inconsistent')

    def test_notificatie_log_exception(self, mock_queue):
        """
        test /notificatie POST:
        check if message was send to subscribers callbackUrls

        """
        kanaal = KanaalFactory.create(naam='zaken', filters=['bron', 'zaaktype', 'vertrouwelijkheidaanduiding'])
        abon = AbonnementFactory.create(callback_url='https://example.com/callback')
        filter_group = FilterGroupFactory.create(kanaal=kanaal, abonnement=abon)
        FilterFactory.create(filter_group=filter_group, key='bron', value='082096752011')
        notificatie_url = reverse('notificaties-list',
                                  kwargs={'version': BASE_REST_FRAMEWORK['DEFAULT_VERSION']})
        request_data = {
            "kanaal": "zaken",
            "hoofdObject": "https://ref.tst.vng.cloud/zrc/api/v1/zaken/d7a22",
            "resource": "status",
            "resourceUrl": "https://ref.tst.vng.cloud/zrc/api/v1/statussen/d7a22/721c9",
            "actie": "create",
            "aanmaakdatum": "2018-01-01T17:00:00Z",
            "kenmerken": {
                "bron": "082096752011",
                "zaaktype": "example.com/api/v1/zaaktypen/5aa5c",
                "vertrouwelijkheidaanduiding": "openbaar",
            }
        }

        with requests_mock.mock() as m:
            m.post(abon.callback_url, exc=requests.exceptions.ConnectTimeout('Timeout exception'))

            response = self.client.post(notificatie_url, request_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(Notificatie.objects.count(), 1)
        self.assertEqual(NotificatieResponse.objects.count(), 1)

        notif_response = NotificatieResponse.objects.get()

        self.assertEqual(notif_response.exception, 'Timeout exception')
