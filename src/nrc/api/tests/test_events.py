from datetime import datetime
from unittest import skip
from unittest.mock import patch
from uuid import uuid4

from django.test import override_settings

from pytz import timezone as pytz_timezone
from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import JWTAuthMixin
from vng_api_common.tests.schema import get_operation_url

from nrc.api.choices import SequencetypeChoices
from nrc.datamodel.models import Event
from nrc.datamodel.tests.factories import DomainFactory, SubscriptionFactory

from ..channels import QueueChannel


@patch("nrc.api.serializers.deliver_message.delay")
@override_settings(
    LINK_FETCHER="vng_api_common.mocks.link_fetcher_200",
    ZDS_CLIENT_CLASS="vng_api_common.mocks.MockClient",
)
class EventsTestCase(JWTAuthMixin, APITestCase):
    heeft_alle_autorisaties = True

    @skip("Sending to RabbitMQ is not currently supported")
    @patch.object(QueueChannel, "send")
    def test_notificatie_send_queue(self, mock_queue, mock_task):
        """
        test /notificatie POST:
        check if message was send to RabbitMQ

        """
        domain = DomainFactory.create(name="nl.vng.zaken")

        uuid = uuid4()
        subscription_uuid = uuid4()

        SubscriptionFactory.create(
            sink="https://example.com/callback",
            domain=domain,
            uuid=str(subscription_uuid),
        )

        event_url = get_operation_url("events_create")

        data = {
            "id": str(uuid),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.status_gewijzigd",
            "time": "2022-03-16T15:29:30.833664Z",
            "subscription": str(subscription_uuid),
            "datacontenttype": "application/json",
            "dataschema": "https://vng.nl/zgw/zaken/status_gewijzigd_schema.json",
            "sequence": "42",
            "sequencetype": SequencetypeChoices.integer,
            "data": {"foo": "bar", "bar": "foo"},
        }

        response = self.client.post(event_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        timezone = pytz_timezone("UTC")
        expected_datetime = timezone.localize(
            datetime.strptime("2022-03-16T15:29:30.833664Z", "%Y-%m-%dT%H:%M:%S.%fZ")
        )

        expected_data = {
            "id": uuid,
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.status_gewijzigd",
            "time": expected_datetime,
            "subscription": subscription_uuid,
            "datacontenttype": "application/json",
            "dataschema": "https://vng.nl/zgw/zaken/status_gewijzigd_schema.json",
            "sequence": "42",
            "sequencetype": SequencetypeChoices.integer,
            "data": {"foo": "bar", "bar": "foo"},
        }

        mock_queue.assert_called_with(expected_data)

    def test_send_simple_event(self, mock_task):
        """
        test /events POST:
        check if message was send to subscribers callbackUrls

        """
        domain = DomainFactory.create(name="nl.vng.zaken")

        uuid = uuid4()
        subscription_uuid = uuid4()

        subscription = SubscriptionFactory.create(
            sink="https://example.com/callback",
            domain=domain,
            uuid=str(subscription_uuid),
        )

        event_url = get_operation_url("events_create")

        data = {
            "id": str(uuid),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.status_gewijzigd",
            "time": "2022-03-16T15:29:30.833664Z",
            "subscription": str(subscription_uuid),
            "datacontenttype": "application/json",
            "dataschema": "https://vng.nl/zgw/zaken/status_gewijzigd_schema.json",
            "sequence": "42",
            "sequencetype": SequencetypeChoices.integer,
            "data": {"foo": "bar", "bar": "foo"},
        }

        response = self.client.post(event_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        event = Event.objects.get()

        timezone = pytz_timezone("UTC")
        expected_datetime = timezone.localize(
            datetime.strptime("2022-03-16T15:29:30.833664Z", "%Y-%m-%dT%H:%M:%S.%fZ")
        )

        expected_data = {
            "id": uuid,
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.status_gewijzigd",
            "time": expected_datetime,
            "subscription": subscription_uuid,
            "datacontenttype": "application/json",
            "dataschema": "https://vng.nl/zgw/zaken/status_gewijzigd_schema.json",
            "sequence": "42",
            "sequencetype": SequencetypeChoices.integer,
            "data": {"foo": "bar", "bar": "foo"},
        }

        mock_task.assert_called_once_with(subscription.id, expected_data, event.id)
