from uuid import uuid4

import requests_mock
from rest_framework.test import APITestCase

from nrc.api.choices import ProtocolMethodChoices, SequencetypeChoices
from nrc.datamodel.tests.factories import (
    DomainFactory,
    EventFactory,
    SubscriptionFactory,
)

from ..tasks import deliver_message


class EventTaskTests(APITestCase):
    def test_simple_task(self):
        subscription = SubscriptionFactory.create(
            domain=DomainFactory(name="nl.vng.zaken"),
            source="urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            sink="https://vng.zaken.nl/callback",
            types=[],
        )

        data = {
            "id": str(uuid4()),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.status_gewijzigd",
            "time": "2022-03-16T15:29:30.833664Z",
            "datacontenttype": "application/json",
            "dataschema": "https://vng.nl/zgw/zaken/status_gewijzigd_schema.json",
            "sequence": "42",
            "sequencetype": SequencetypeChoices.integer,
            "data": {"foo": "bar", "bar": "foo"},
        }

        event = EventFactory.create(forwarded_msg=data, domain=subscription.domain)

        with requests_mock.mock() as m:
            m.post(subscription.sink)

            deliver_message(event.id)

        self.assertEqual(m.last_request.url, subscription.sink)
        self.assertEqual(m.last_request.json(), data)

    def test_no_matching_subscriptions(self):
        domain = DomainFactory(name="nl.vng.zaken")

        # Different domain
        SubscriptionFactory.create(
            domain=DomainFactory(name="nl.vng.documenten"),
            source="urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            sink="https://vng.zaken.nl/callback",
            types=[],
        )

        # different source
        SubscriptionFactory.create(
            domain=domain,
            source="urn:nld:oin:000000012345678910000:systeem:Zaaksysteem",
            sink="https://vng.zaken.nl/callback",
            types=[],
        )

        # different types
        SubscriptionFactory.create(
            domain=domain,
            source="urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            sink="https://vng.zaken.nl/callback",
            types=["nl.vng.zaken.status_verlengd"],
        )

        data = {
            "id": str(uuid4()),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.status_gewijzigd",
            "time": "2022-03-16T15:29:30.833664Z",
            "datacontenttype": "application/json",
            "dataschema": "https://vng.nl/zgw/zaken/status_gewijzigd_schema.json",
            "sequence": "42",
            "sequencetype": SequencetypeChoices.integer,
            "data": {"foo": "bar", "bar": "foo"},
        }

        event = EventFactory.create(forwarded_msg=data, domain=domain)

        with requests_mock.mock() as m:
            m.post(requests_mock.ANY)
            deliver_message(event.id)

        self.assertEqual(m.request_history, [])

    def test_matching_types(self):
        domain = DomainFactory(name="nl.vng.zaken")

        SubscriptionFactory.create(
            domain=domain,
            source="urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            sink="https://vng.zaken.nl/callback",
            types=[],
        )

        SubscriptionFactory.create(
            domain=domain,
            source="urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            sink="https://vng.zaken.eu/callback",
            types=["nl.vng.zaken.status_gewijzigd", "nl.vng.zaken.status_verlengd"],
        )

        SubscriptionFactory.create(
            domain=None,
            source="urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            sink="https://vng.generiek.nl/callback",
            types=[],
        )

        data = {
            "id": str(uuid4()),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.status_gewijzigd",
            "time": "2022-03-16T15:29:30.833664Z",
            "datacontenttype": "application/json",
            "dataschema": "https://vng.nl/zgw/zaken/status_gewijzigd_schema.json",
            "sequence": "42",
            "sequencetype": SequencetypeChoices.integer,
            "data": {"foo": "bar", "bar": "foo"},
        }

        event = EventFactory.create(forwarded_msg=data, domain=domain)

        expected_urls = (
            "https://vng.zaken.nl/callback",
            "https://vng.zaken.eu/callback",
            "https://vng.generiek.nl/callback",
        )

        with requests_mock.mock() as m:
            m.post(
                requests_mock.ANY,
                additional_matcher=lambda request: request.url in expected_urls,
            )

            deliver_message(event.id)

        self.assertEqual(m.call_count, 3)

        first_request = m.request_history[0]

        self.assertEqual(first_request.url, "https://vng.zaken.nl/callback")
        self.assertEqual(first_request.json(), data)

        second_request = m.request_history[1]

        self.assertEqual(second_request.url, "https://vng.zaken.eu/callback")
        self.assertEqual(second_request.json(), data)

        third_request = m.request_history[2]

        self.assertEqual(third_request.url, "https://vng.generiek.nl/callback")
        self.assertEqual(third_request.json(), data)

    def test_sink_credential(self):
        domain = DomainFactory(name="nl.vng.zaken")

        SubscriptionFactory.create(
            domain=domain,
            source="urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            sink="https://vng.zaken.nl/callback",
            sink_credential={
                "credential_type": "ACCESSTOKEN",
                "access_token": "FOOBAR",
                "access_token_expires_utc": "2042-05-25 14:23:53.119Z",
                "access_token_type": "bearer",
            },
        )

        SubscriptionFactory.create(
            domain=domain,
            source="urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            sink="https://vng.zaken.eu/callback",
            sink_credential={
                "credential_type": "ACCESSTOKEN",
                "access_token": "BARFOO",
                "access_token_expires_utc": "2042-05-25 14:23:53.119Z",
                "access_token_type": "bearer",
            },
        )

        data = {
            "id": str(uuid4()),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.status_gewijzigd",
            "time": "2022-03-16T15:29:30.833664Z",
            "datacontenttype": "application/json",
            "dataschema": "https://vng.nl/zgw/zaken/status_gewijzigd_schema.json",
            "sequence": "42",
            "sequencetype": SequencetypeChoices.integer,
            "data": {"foo": "bar", "bar": "foo"},
        }

        event = EventFactory.create(forwarded_msg=data, domain=domain)

        expected_urls = (
            "https://vng.zaken.nl/callback",
            "https://vng.zaken.eu/callback",
        )

        with requests_mock.mock() as m:
            m.post(
                requests_mock.ANY,
                additional_matcher=lambda request: request.url in expected_urls,
            )

            deliver_message(event.id)

        self.assertEqual(m.call_count, 2)

        first_request = m.request_history[0]

        self.assertEqual(first_request.url, "https://vng.zaken.nl/callback")
        self.assertEqual(first_request.json(), data)
        self.assertEqual(first_request.headers["Authorization"], "bearer FOOBAR")

        second_request = m.request_history[1]

        self.assertEqual(second_request.url, "https://vng.zaken.eu/callback")
        self.assertEqual(second_request.json(), data)
        self.assertEqual(second_request.headers["Authorization"], "bearer BARFOO")

    def test_protocol_settings(self):
        domain = DomainFactory(name="nl.vng.zaken")

        SubscriptionFactory.create(
            domain=domain,
            source="urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            sink="https://vng.zaken.nl/callback",
            protocol_settings={
                "headers": {
                    "X-Custom-Header-X": "value X",
                    "X-Custom-Header-Y": "value Y",
                },
                "method": ProtocolMethodChoices.post.value,
            },
        )

        SubscriptionFactory.create(
            domain=domain,
            source="urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            sink="https://vng.zaken.eu/callback",
            protocol_settings={
                "headers": {
                    "X-Custom-Header-Y": "value Y",
                    "X-Custom-Header-Z": "value Z",
                },
                "method": ProtocolMethodChoices.post.value,
            },
        )

        data = {
            "id": str(uuid4()),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.status_gewijzigd",
            "time": "2022-03-16T15:29:30.833664Z",
            "datacontenttype": "application/json",
            "dataschema": "https://vng.nl/zgw/zaken/status_gewijzigd_schema.json",
            "sequence": "42",
            "sequencetype": SequencetypeChoices.integer,
            "data": {"foo": "bar", "bar": "foo"},
        }

        event = EventFactory.create(forwarded_msg=data, domain=domain)

        expected_urls = (
            "https://vng.zaken.nl/callback",
            "https://vng.zaken.eu/callback",
        )

        with requests_mock.mock() as m:
            m.post(
                requests_mock.ANY,
                additional_matcher=lambda request: request.url in expected_urls,
            )

            deliver_message(event.id)

        self.assertEqual(m.call_count, 2)

        first_request = m.request_history[0]

        self.assertEqual(first_request.url, "https://vng.zaken.nl/callback")
        self.assertEqual(first_request.json(), data)
        self.assertEqual(first_request.headers["X-Custom-Header-X"], "value X")
        self.assertEqual(first_request.headers["X-Custom-Header-Y"], "value Y")

        second_request = m.request_history[1]

        self.assertEqual(second_request.url, "https://vng.zaken.eu/callback")
        self.assertEqual(second_request.json(), data)
        self.assertEqual(second_request.headers["X-Custom-Header-Y"], "value Y")
        self.assertEqual(second_request.headers["X-Custom-Header-Z"], "value Z")

    def test_sink_credential_protocol_settings_precedence(self):
        """
        Sink credential headers should have a higher precedence then protocol_settings
        """
        subscription = SubscriptionFactory.create(
            domain=DomainFactory(name="nl.vng.zaken"),
            source="urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            sink="https://vng.zaken.nl/callback",
            sink_credential={
                "credential_type": "ACCESSTOKEN",
                "access_token": "FOOBAR",
                "access_token_expires_utc": "2042-05-25 14:23:53.119Z",
                "access_token_type": "bearer",
            },
            protocol_settings={
                "headers": {
                    "Authorization": "bearer I-SHOULD-NOT-BE-USED",
                    "X-Custom-Header-Y": "value Y",
                    "X-Custom-Header-Z": "value Z",
                },
                "method": ProtocolMethodChoices.post.value,
            },
        )

        data = {
            "id": str(uuid4()),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.status_gewijzigd",
            "time": "2022-03-16T15:29:30.833664Z",
            "datacontenttype": "application/json",
            "dataschema": "https://vng.nl/zgw/zaken/status_gewijzigd_schema.json",
            "sequence": "42",
            "sequencetype": SequencetypeChoices.integer,
            "data": {"foo": "bar", "bar": "foo"},
        }

        event = EventFactory.create(forwarded_msg=data, domain=subscription.domain)

        with requests_mock.mock() as m:
            m.post(subscription.sink)

            deliver_message(event.id)

        self.assertEqual(m.last_request.url, subscription.sink)
        self.assertEqual(m.last_request.json(), data)
        self.assertEqual(m.last_request.headers["Authorization"], "bearer FOOBAR")
        self.assertEqual(m.last_request.headers["X-Custom-Header-Y"], "value Y")
        self.assertEqual(m.last_request.headers["X-Custom-Header-Z"], "value Z")


class EventTaskFilterAttributeTests(APITestCase):
    def test_domain_matching_filter_attributes(self):
        domain = DomainFactory.create(
            name="nl.vng.zaken",
            filter_attributes=["bronorganisatie", "vertrouwelijkheid"],
        )
        subscription = SubscriptionFactory.create(
            domain=domain,
            source="urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            sink="https://vng.zaken.nl/callback",
            types=[],
        )

        data = {
            "id": str(uuid4()),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.status_gewijzigd",
            "time": "2022-03-16T15:29:30.833664Z",
            "datacontenttype": "application/json",
            "dataschema": "https://vng.nl/zgw/zaken/status_gewijzigd_schema.json",
            "sequence": "42",
            "sequencetype": SequencetypeChoices.integer,
            "data": {"foo": "bar", "bar": "foo"},
            "vertrouwelijkheid": "VERTOUWELIJK",
        }

        event = EventFactory.create(forwarded_msg=data, domain=subscription.domain)

        with requests_mock.mock() as m:
            m.post(subscription.sink)

            deliver_message(event.id)

        self.assertEqual(m.last_request.url, subscription.sink)
        self.assertEqual(m.last_request.json(), data)

    def test_domain_no_matching_filter_attributes(self):
        domain = DomainFactory.create(
            name="nl.vng.zaken",
            filter_attributes=["bronorganisatie", "vertrouwelijkheid"],
        )
        subscription = SubscriptionFactory.create(
            domain=domain,
            source="urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            sink="https://vng.zaken.nl/callback",
            types=[],
        )

        data = {
            "id": str(uuid4()),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.status_gewijzigd",
            "time": "2022-03-16T15:29:30.833664Z",
            "datacontenttype": "application/json",
            "dataschema": "https://vng.nl/zgw/zaken/status_gewijzigd_schema.json",
            "sequence": "42",
            "sequencetype": SequencetypeChoices.integer,
            "data": {"foo": "bar", "bar": "foo"},
            "zaakType": "https://vng.zaken.nl/zakentypen/xyz",
        }

        event = EventFactory.create(forwarded_msg=data, domain=subscription.domain)

        with requests_mock.mock() as m:
            m.post(subscription.sink)

            deliver_message(event.id)

        self.assertEqual(m.request_history, [])

    def test_domain_mismatch_filter_attributes(self):
        """
        An Event having more custom attributes then specified in its filter_attributes
        should not be sent to subscriptions coupled to the given domain.
        """
        domain = DomainFactory.create(
            name="nl.vng.zaken",
            filter_attributes=["bronorganisatie", "vertrouwelijkheid"],
        )
        subscription = SubscriptionFactory.create(
            domain=domain,
            source="urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            sink="https://vng.zaken.nl/callback",
            types=[],
        )

        data = {
            "id": str(uuid4()),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.status_gewijzigd",
            "time": "2022-03-16T15:29:30.833664Z",
            "datacontenttype": "application/json",
            "dataschema": "https://vng.nl/zgw/zaken/status_gewijzigd_schema.json",
            "sequence": "42",
            "sequencetype": SequencetypeChoices.integer,
            "data": {"foo": "bar", "bar": "foo"},
            "bronorganisatie": "Organisatie Y",
            "vertrouwelijkheid": "VERTOUWELIJK",
            "customAttribute": "custom value",
        }

        event = EventFactory.create(forwarded_msg=data, domain=subscription.domain)

        with requests_mock.mock() as m:
            m.post(subscription.sink)

            deliver_message(event.id)

        self.assertEqual(m.request_history, [])

    def test_domain_no_filter_attributes(self):
        """
        Specifing no filter_attributes should sent all incoming events with
        custom attributes.
        """
        domain = DomainFactory(name="nl.vng.zaken", filter_attributes=[])
        subscription = SubscriptionFactory.create(
            domain=domain,
            source="urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            sink="https://vng.zaken.nl/callback",
            types=[],
        )

        data = {
            "id": str(uuid4()),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.status_gewijzigd",
            "time": "2022-03-16T15:29:30.833664Z",
            "datacontenttype": "application/json",
            "dataschema": "https://vng.nl/zgw/zaken/status_gewijzigd_schema.json",
            "sequence": "42",
            "sequencetype": SequencetypeChoices.integer,
            "data": {"foo": "bar", "bar": "foo"},
            "bronorganisatie": "Organisatie X",
            "vertrouwelijkheid": "VERTOUWELIJK",
        }

        event = EventFactory.create(forwarded_msg=data, domain=subscription.domain)

        with requests_mock.mock() as m:
            m.post(subscription.sink)

            deliver_message(event.id)

        self.assertEqual(m.last_request.url, subscription.sink)
        self.assertEqual(m.last_request.json(), data)
