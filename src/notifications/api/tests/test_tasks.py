from unittest.mock import patch

import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase

from notifications.datamodel.models import NotificatieResponse
from notifications.datamodel.tests.factories import (
    AbonnementFactory, NotificatieFactory
)

from ..tasks import send_msg_to_sub


class NotifCeleryTests(APITestCase):
    @patch('notifications.api.tasks.requests.post',
           return_value=Response(status=status.HTTP_201_CREATED))
    def test_notificatie_task_send_abonnement(self, mock_send):
        """
        test /notificatie POST:
        check if message was send to subscribers callbackUrls

        """
        abon = AbonnementFactory.create()
        notif = NotificatieFactory.create()

        request_data = {
            "kanaal": "zaken",
            "hoofdObject": "https://ref.tst.vng.cloud/zrc/api/v1/zaken/d7a22",
            "resource": "status",
            "resourceUrl": "https://ref.tst.vng.cloud/zrc/api/v1/statussen/d7a22/721c9",
            "actie": "create",
            "aanmaakdatum": "2018-01-01T17:00:00Z",
            "kenmerken": [
                {"bron": "082096752011"},
                {"zaaktype": "example.com/api/v1/zaaktypen/5aa5c"},
                {"vertrouwelijkheidaanduiding": "openbaar"}
            ]
        }

        status_code = send_msg_to_sub(abon.id, request_data, notif.id)

        self.assertEqual(status_code, status.HTTP_201_CREATED)

        mock_args, mock_kwargs = mock_send.call_args

        self.assertEqual(mock_args[0], abon.callback_url)
        self.assertEqual(mock_kwargs['data'], request_data)
        self.assertEqual(mock_kwargs['headers']['Content-Type'], 'application/json')
        self.assertEqual(mock_kwargs['headers']['Authorization'], abon.auth)

    @patch('notifications.api.tasks.requests.post',
           return_value=Response(status=status.HTTP_201_CREATED))
    def test_notificatie_task_log(self, mock_send):
        """
        test /notificatie POST:
        check if message was send to subscribers callbackUrls

        """
        abon = AbonnementFactory.create()
        notif = NotificatieFactory.create()

        request_data = {
            "kanaal": "zaken",
            "hoofdObject": "https://ref.tst.vng.cloud/zrc/api/v1/zaken/d7a22",
            "resource": "status",
            "resourceUrl": "https://ref.tst.vng.cloud/zrc/api/v1/statussen/d7a22/721c9",
            "actie": "create",
            "aanmaakdatum": "2018-01-01T17:00:00Z",
            "kenmerken": [
                {"bron": "082096752011"},
                {"zaaktype": "example.com/api/v1/zaaktypen/5aa5c"},
                {"vertrouwelijkheidaanduiding": "openbaar"}
            ]
        }

        status_code = send_msg_to_sub(abon.id, request_data, notif.id)

        self.assertEqual(status_code, status.HTTP_201_CREATED)
        self.assertEqual(NotificatieResponse.objects.count(), 1)

        notif_response = NotificatieResponse.objects.get()

        self.assertEqual(notif_response.response_status, '201')
        self.assertEqual(notif_response.exception, '')

    @patch('notifications.api.tasks.requests.post',
           side_effect=requests.exceptions.ConnectTimeout('Timeout exception'))
    def test_notificatie_log_exception(self, mock_send):
        """
        test /notificatie POST:
        check if message was send to subscribers callbackUrls

        """
        abon = AbonnementFactory.create()
        notif = NotificatieFactory.create()

        request_data = {
            "kanaal": "zaken",
            "hoofdObject": "https://ref.tst.vng.cloud/zrc/api/v1/zaken/d7a22",
            "resource": "status",
            "resourceUrl": "https://ref.tst.vng.cloud/zrc/api/v1/statussen/d7a22/721c9",
            "actie": "create",
            "aanmaakdatum": "2018-01-01T17:00:00Z",
            "kenmerken": [
                {"bron": "082096752011"},
                {"zaaktype": "example.com/api/v1/zaaktypen/5aa5c"},
                {"vertrouwelijkheidaanduiding": "openbaar"}
            ]
        }

        status_code = send_msg_to_sub(abon.id, request_data, notif.id)

        self.assertIsNone(status_code)
        self.assertEqual(NotificatieResponse.objects.count(), 1)

        notif_response = NotificatieResponse.objects.get()

        self.assertEqual(notif_response.exception, 'Timeout exception')
