import json

from django.core.serializers.json import DjangoJSONEncoder

import requests
import requests_mock
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase

from notifications.datamodel.models import NotificatieResponse
from notifications.datamodel.tests.factories import (
    AbonnementFactory, NotificatieFactory
)

from ..tasks import deliver_message


class NotifCeleryTests(APITestCase):
    def test_notificatie_task_send_abonnement(self):
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
            "kenmerken": {
                "bron": "082096752011",
                "zaaktype": "example.com/api/v1/zaaktypen/5aa5c",
                "vertrouwelijkheidaanduiding": "openbaar"
            }
        }
        msg = json.dumps(request_data, cls=DjangoJSONEncoder)

        with requests_mock.mock() as m:
            m.post(abon.callback_url)

            deliver_message(abon.id, msg, notif.id)

        self.assertEqual(m.last_request.url, abon.callback_url)
        self.assertEqual(m.last_request.body, msg)
        self.assertEqual(m.last_request.headers['Content-Type'], 'application/json')
        self.assertEqual(m.last_request.headers['Authorization'], abon.auth)

    def test_notificatie_task_log(self):
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
            "kenmerken": {
                "bron": "082096752011",
                "zaaktype": "example.com/api/v1/zaaktypen/5aa5c",
                "vertrouwelijkheidaanduiding": "openbaar"
            }
        }
        msg = json.dumps(request_data, cls=DjangoJSONEncoder)

        with requests_mock.mock() as m:
            m.post(abon.callback_url, status_code=201)

            deliver_message(abon.id, msg, notif.id)

        self.assertEqual(NotificatieResponse.objects.count(), 1)

        notif_response = NotificatieResponse.objects.get()

        self.assertEqual(notif_response.response_status, '201')
        self.assertEqual(notif_response.exception, '')

    def test_notificatie_log_exception(self):
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
            "kenmerken": {
                "bron": "082096752011",
                "zaaktype": "example.com/api/v1/zaaktypen/5aa5c",
                "vertrouwelijkheidaanduiding": "openbaar"
            }
        }
        msg = json.dumps(request_data, cls=DjangoJSONEncoder)

        with requests_mock.mock() as m:
            m.post(abon.callback_url, exc=requests.exceptions.ConnectTimeout('Timeout exception'))

            deliver_message(abon.id, msg, notif.id)

        self.assertEqual(NotificatieResponse.objects.count(), 1)

        notif_response = NotificatieResponse.objects.get()

        self.assertEqual(notif_response.exception, 'Timeout exception')
