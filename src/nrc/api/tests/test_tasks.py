from uuid import uuid4

import requests
import requests_mock
from rest_framework.test import APITestCase

from nrc.api.choices import SequencetypeChoices
from nrc.datamodel.models import EventResponse
from nrc.datamodel.tests.factories import (
    DomainFactory,
    EventFactory,
    SubscriptionFactory,
)

from ..tasks import deliver_message


# TODO: test correct behaviour for subscription field
class NotifCeleryTests(APITestCase):
    def test_event_task_send_subscriptions(self):
        uuid = uuid4()
        subscription_uuid = uuid4()

        domain = DomainFactory.create(name="nl.vng.zaken")
        subscription = SubscriptionFactory.create(
            sink="https://example.com/callback",
            domain=domain,
            uuid=str(subscription_uuid),
            protocol_settings={
                "headers": {
                    "Authorization": "bearer secrit-token",
                    "X-Custom-Header": "Foobar",
                },
                "method": "POST",
            },
        )

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

        event = EventFactory.create(forwarded_msg=data)

        with requests_mock.mock() as m:
            m.post(subscription.sink)

            deliver_message(subscription.id, data, event.id)

        self.assertEqual(m.last_request.url, subscription.sink)
        self.assertEqual(m.last_request.json(), data)

        self.assertEqual(m.last_request.headers["Authorization"], "bearer secrit-token")
        self.assertEqual(m.last_request.headers["X-Custom-Header"], "Foobar")
        self.assertEqual(m.last_request.headers["Content-Type"], "application/json")

    def test_event_task_log(self):
        uuid = uuid4()
        subscription_uuid = uuid4()

        domain = DomainFactory.create(name="nl.vng.zaken")
        subscription = SubscriptionFactory.create(
            sink="https://example.com/callback",
            domain=domain,
            uuid=str(subscription_uuid),
        )

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

        event = EventFactory.create(forwarded_msg=data)

        with requests_mock.mock() as m:
            m.post(subscription.sink, status_code=201)

            deliver_message(subscription.id, data, event.id)

        event_response = EventResponse.objects.get()

        self.assertEqual(event_response.response_status, 201)
        self.assertEqual(event_response.exception, "")

    def test_event_log_exception(self):
        uuid = uuid4()
        subscription_uuid = uuid4()

        domain = DomainFactory.create(name="nl.vng.zaken")
        subscription = SubscriptionFactory.create(
            sink="https://example.com/callback",
            domain=domain,
            uuid=str(subscription_uuid),
        )

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

        event = EventFactory.create(forwarded_msg=data)

        with requests_mock.mock() as m:
            m.post(
                subscription.sink,
                exc=requests.exceptions.ConnectTimeout("Timeout exception"),
            )

            deliver_message(subscription.id, data, event.id)

        event_response = EventResponse.objects.get()

        self.assertEqual(event_response.response_status, None)
        self.assertEqual(event_response.exception, "Timeout exception")
