from unittest.mock import patch
from uuid import uuid4

from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import JWTAuthMixin
from vng_api_common.tests.schema import get_operation_url

from nrc.api.choices import SequencetypeChoices
from nrc.datamodel.models import Event
from nrc.datamodel.tests.factories import DomainFactory


@patch("nrc.api.serializers.deliver_message.delay")
@override_settings(
    LINK_FETCHER="vng_api_common.mocks.link_fetcher_200",
    ZDS_CLIENT_CLASS="vng_api_common.mocks.MockClient",
)
class EventsTestCase(JWTAuthMixin, APITestCase):
    heeft_alle_autorisaties = True

    def test_send_simple_event(self, mocked_task):
        """
        test /events POST:
        check if message was send to subscribers callbackUrls

        """
        DomainFactory.create(name="nl.vng.zaken")

        event_uuid = uuid4()

        data = {
            "id": str(event_uuid),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.status_gewijzigd",
            "time": "2022-05-25T10:57:19.498Z",
            "datacontenttype": "application/json",
            "dataschema": "https://vng.nl/zgw/zaken/status_gewijzigd_schema.json",
            "sequence": "42",
            "sequencetype": SequencetypeChoices.integer.value,
            "data": {"foo": "bar", "bar": "foo"},
        }

        event_url = get_operation_url("events_create")

        response = self.client.post(event_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertNotIn("Location", response.headers)

        event = Event.objects.get()

        self.assertEqual(event.forwarded_msg, data)

        mocked_task.assert_called_once_with(event.id)
