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
        self.assertEqual(
            m.last_request.json(), {**data, "subscription": str(subscription.uuid)}
        )

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

        subscription_1 = SubscriptionFactory.create(
            domain=domain,
            source="urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            sink="https://vng.zaken.nl/callback",
            types=[],
        )

        subscription_2 = SubscriptionFactory.create(
            domain=domain,
            source="urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            sink="https://vng.zaken.eu/callback",
            types=["nl.vng.zaken.status_gewijzigd", "nl.vng.zaken.status_verlengd"],
        )

        subscription_3 = SubscriptionFactory.create(
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

        self.assertEqual(first_request.url, "https://vng.generiek.nl/callback")
        self.assertEqual(
            first_request.json(), {**data, "subscription": str(subscription_3.uuid)}
        )

        second_request = m.request_history[1]

        self.assertEqual(second_request.url, "https://vng.zaken.eu/callback")
        self.assertEqual(
            second_request.json(), {**data, "subscription": str(subscription_2.uuid)}
        )

        third_request = m.request_history[2]

        self.assertEqual(third_request.url, "https://vng.zaken.nl/callback")
        self.assertEqual(
            third_request.json(), {**data, "subscription": str(subscription_1.uuid)}
        )

    def test_sink_credential(self):
        domain = DomainFactory(name="nl.vng.zaken")

        subscription_1 = SubscriptionFactory.create(
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

        subscription_2 = SubscriptionFactory.create(
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

        self.assertEqual(first_request.url, "https://vng.zaken.eu/callback")
        self.assertEqual(
            first_request.json(), {**data, "subscription": str(subscription_2.uuid)}
        )
        self.assertEqual(first_request.headers["Authorization"], "bearer BARFOO")

        second_request = m.request_history[1]

        self.assertEqual(second_request.url, "https://vng.zaken.nl/callback")
        self.assertEqual(
            second_request.json(), {**data, "subscription": str(subscription_1.uuid)}
        )
        self.assertEqual(second_request.headers["Authorization"], "bearer FOOBAR")

    def test_protocol_settings(self):
        domain = DomainFactory(name="nl.vng.zaken")

        subscription_1 = SubscriptionFactory.create(
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

        subscription_2 = SubscriptionFactory.create(
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

        self.assertEqual(first_request.url, "https://vng.zaken.eu/callback")
        self.assertEqual(
            first_request.json(), {**data, "subscription": str(subscription_2.uuid)}
        )
        self.assertEqual(first_request.headers["X-Custom-Header-Y"], "value Y")
        self.assertEqual(first_request.headers["X-Custom-Header-Z"], "value Z")

        second_request = m.request_history[1]

        self.assertEqual(second_request.url, "https://vng.zaken.nl/callback")
        self.assertEqual(
            second_request.json(), {**data, "subscription": str(subscription_1.uuid)}
        )
        self.assertEqual(second_request.headers["X-Custom-Header-X"], "value X")
        self.assertEqual(second_request.headers["X-Custom-Header-Y"], "value Y")

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
        self.assertEqual(
            m.last_request.json(), {**data, "subscription": str(subscription.uuid)}
        )
        self.assertEqual(m.last_request.headers["Authorization"], "bearer FOOBAR")
        self.assertEqual(m.last_request.headers["X-Custom-Header-Y"], "value Y")
        self.assertEqual(m.last_request.headers["X-Custom-Header-Z"], "value Z")

    def test_subscribers_reference(self):
        subscriber_reference = uuid4()

        subscription = SubscriptionFactory.create(
            domain=DomainFactory(name="nl.vng.zaken"),
            source="urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            subscriber_reference=str(subscriber_reference),
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
            "subscriberReference": str(uuid4()),
            "sequence": "42",
            "sequencetype": SequencetypeChoices.integer,
            "data": {"foo": "bar", "bar": "foo"},
        }

        event = EventFactory.create(forwarded_msg=data, domain=subscription.domain)

        with requests_mock.mock() as m:
            m.post(subscription.sink)

            deliver_message(event.id)

        self.assertEqual(m.last_request.url, subscription.sink)
        self.assertEqual(
            m.last_request.json(),
            {
                **data,
                "subscription": str(subscription.uuid),
                "subscriberReference": str(subscriber_reference),
            },
        )

    def test_subscription_without_subscriber_reference(self):
        """
        Tests that subscriberReference is omitted when an subscription does not
        have a value for it.
        """
        subscription = SubscriptionFactory.create(
            domain=DomainFactory(name="nl.vng.zaken"),
            source="urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            subscriber_reference=None,
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
            "subscriberReference": str(uuid4()),
            "sequence": "42",
            "sequencetype": SequencetypeChoices.integer,
            "data": {"foo": "bar", "bar": "foo"},
        }

        event = EventFactory.create(forwarded_msg=data, domain=subscription.domain)

        with requests_mock.mock() as m:
            m.post(subscription.sink)

            deliver_message(event.id)

        self.assertEqual(m.last_request.url, subscription.sink)
        self.assertEqual(
            m.last_request.json(),
            {
                **{
                    key: value
                    for key, value in data.items()
                    if key != "subscriberReference"
                },
                "subscription": str(subscription.uuid),
            },
        )

    def test_non_camelcase_rendering(self):
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
            "custom_key_with_underscores": "foo",
            "customKeyWithCamelCase": "foo",
            "custom_key_with_Ugly_Formatting": "boo",
        }

        event = EventFactory.create(forwarded_msg=data, domain=subscription.domain)

        with requests_mock.mock() as m:
            m.post(subscription.sink)

            deliver_message(event.id)

        self.assertEqual(m.last_request.url, subscription.sink)
        self.assertEqual(
            m.last_request.json(), {**data, "subscription": str(subscription.uuid)}
        )

    def test_no_source(self):
        subscription = SubscriptionFactory.create(
            domain=DomainFactory(name="nl.vng.zaken"),
            sink="https://vng.zaken.nl/callback",
            source=None,
            types=None,
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
            "custom_key_with_underscores": "foo",
            "customKeyWithCamelCase": "foo",
            "custom_key_with_Ugly_Formatting": "boo",
        }

        event_1 = EventFactory.create(forwarded_msg=data, domain=subscription.domain)

        event_2 = EventFactory.create(
            forwarded_msg={
                **data,
                "id": str(uuid4()),
                # different source
                "source": "urn:nld:oin:00000001234567890000:client:Zaaksysteem",
            },
            domain=subscription.domain,
        )

        with requests_mock.mock() as m:
            m.post(subscription.sink)

            for event in (
                event_1,
                event_2,
            ):
                deliver_message(event.id)

        self.assertEqual(len(m.request_history), 2)
        self.assertCountEqual(
            set(request.url for request in m.request_history), (subscription.sink,)
        )


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
        self.assertEqual(
            m.last_request.json(), {**data, "subscription": str(subscription.uuid)}
        )

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
        self.assertEqual(
            m.last_request.json(), {**data, "subscription": str(subscription.uuid)}
        )

    def test_custom_field_filter_attribute_matching(self):
        """
        Test that events with custom attributes with and without camelcase formatting
        are filtered correctly by the subscription's domain filter attributes value.
        """
        domain = DomainFactory.create(
            name="nl.vng.zaken",
            filter_attributes=[
                "vertrouwelijkheid",
                "custom_key_with_underscores",
                "customKeyWithCamelCase",
                "custom_key_with_Ugly_Formatting",
            ],
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
            "custom_key_with_underscores": "foo",
            "customKeyWithCamelCase": "foo",
            "custom_key_with_Ugly_Formatting": "boo",
        }

        event = EventFactory.create(forwarded_msg=data, domain=subscription.domain)

        with requests_mock.mock() as m:
            m.post(subscription.sink)

            deliver_message(event.id)

        self.assertEqual(m.last_request.url, subscription.sink)
        self.assertEqual(
            m.last_request.json(), {**data, "subscription": str(subscription.uuid)}
        )


class EventCustomFilterTests(APITestCase):
    def test_simple_all_filter(self):
        domain = DomainFactory(name="nl.vng.zaken")

        subscription = SubscriptionFactory.create(
            sink="https://vng.zaken.nl/callback",
            filters=[
                {
                    "exact": {
                        "domain": "nl.vng.zaken",
                        "vertrouwelijk": "normaal",
                    },
                },
                {
                    "exact": {
                        "type": "nl.vng.zaken.zaak_gesloten",
                    },
                },
            ],
            domain=None,
            source=None,
        )

        data = {
            "id": str(uuid4()),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.zaak_gesloten",
            "vertrouwelijk": "normaal",
            "data": {"foo": "bar", "bar": "foo"},
        }

        matching_event = EventFactory.create(forwarded_msg=data, domain=domain)
        mismatching_event = EventFactory.create(
            forwarded_msg={**data, "vertrouwelijk": "hoog"}, domain=domain
        )

        with requests_mock.mock() as m:
            m.post(subscription.sink)
            deliver_message(matching_event.id)
            deliver_message(mismatching_event.id)

        self.assertEqual(len(m.request_history), 1)

        self.assertEqual(m.last_request.url, subscription.sink)
        self.assertEqual(
            m.last_request.json(), {**data, "subscription": str(subscription.uuid)}
        )

    def test_simple_any_filter(self):
        domain = DomainFactory(name="nl.vng.zaken")

        subscription = SubscriptionFactory.create(
            sink="https://vng.zaken.nl/callback",
            filters=[
                {
                    "exact": {
                        "domain": "nl.vng.zaken",
                    },
                },
                {
                    "any": [
                        {
                            "exact": {
                                "type": "nl.vng.zaken.zaak_gesloten",
                            },
                        },
                        {
                            "exact": {
                                "type": "nl.vng.zaken.zaak_geopend",
                            },
                        },
                    ],
                },
            ],
            domain=None,
            source=None,
        )

        data = {
            "id": str(uuid4()),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.zaak_gesloten",
            "data": {"foo": "bar", "bar": "foo"},
        }

        matching_event_1 = EventFactory.create(forwarded_msg=data, domain=domain)
        matching_event_2 = EventFactory.create(
            forwarded_msg={**data, "type": "nl.vng.zaken.zaak_geopend"}, domain=domain
        )
        mismatching_event = EventFactory.create(
            forwarded_msg={**data, "type": "nl.vng.zaken.status_gewijzigd"},
            domain=domain,
        )

        with requests_mock.mock() as m:
            m.post(subscription.sink)

            deliver_message(matching_event_1.id)
            deliver_message(matching_event_2.id)
            deliver_message(mismatching_event.id)

        self.assertEqual(len(m.request_history), 2)

        self.assertEqual(m.last_request.url, subscription.sink)

        first_request = m.request_history[0]

        self.assertEqual(
            first_request.json(), {**data, "subscription": str(subscription.uuid)}
        )

        second_request = m.request_history[1]

        self.assertEqual(
            second_request.json(),
            {
                **data,
                "subscription": str(subscription.uuid),
                "type": "nl.vng.zaken.zaak_geopend",
            },
        )

    def test_complex_any_filter(self):
        domain = DomainFactory(name="nl.vng.zaken")
        mismatching_domain = DomainFactory(name="nl.vng.documenten")

        subscription = SubscriptionFactory.create(
            sink="https://vng.zaken.nl/callback",
            filters=[
                {
                    "any": [
                        {
                            "all": [
                                {
                                    "exact": {
                                        "domain": "nl.vng.zaken",
                                        "vertrouwelijk": "hoog",
                                    },
                                },
                                {
                                    "any": [
                                        {
                                            "exact": {
                                                "type": "nl.vng.zaken.zaak_gesloten",
                                            },
                                        },
                                        {
                                            "exact": {
                                                "type": "nl.vng.zaken.zaak_geopend",
                                            },
                                        },
                                    ],
                                },
                            ],
                        },
                        {
                            "all": [
                                {
                                    "exact": {
                                        "domain": "nl.vng.burgerzaken",
                                        "vertrouwelijk": "normaal",
                                    },
                                },
                                {
                                    "exact": {
                                        "type": "nl.vng.burgerzaken.kind_geboren_aangifte_elders",
                                    },
                                },
                            ],
                        },
                    ],
                },
            ],
            domain=None,
            source=None,
        )

        data = {
            "id": str(uuid4()),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.zaak_gesloten",
            "vertrouwelijk": "hoog",
            "data": {"foo": "bar", "bar": "foo"},
        }

        matching_event_1 = EventFactory.create(forwarded_msg=data, domain=domain)
        matching_event_2 = EventFactory.create(
            forwarded_msg={
                **data,
                "type": "nl.vng.zaken.zaak_geopend",
            },
            domain=domain,
        )
        matching_event_3 = EventFactory.create(
            forwarded_msg={
                **data,
                "domain": "nl.vng.burgerzaken",
                "type": "nl.vng.burgerzaken.kind_geboren_aangifte_elders",
                "vertrouwelijk": "normaal",
            },
            domain=domain,
        )


        mismatching_event_1 = EventFactory.create(
            forwarded_msg={**data, "type": "nl.vng.zaken.status_gewijzigd"},
            domain=domain,
        )

        mismatching_event_2 = EventFactory.create(
            # different domain
            forwarded_msg={**data, "domain": "nl.vng.documenten"},
            domain=mismatching_domain,
        )
        mismatching_event_3 = EventFactory.create(
            # different vertrouwelijk
            forwarded_msg={**data, "vertrouwelijk": "normaal"},
            domain=mismatching_domain,
        )

        with requests_mock.mock() as m:
            m.post(subscription.sink)

            deliver_message(matching_event_1.id)
            deliver_message(matching_event_2.id)
            deliver_message(matching_event_3.id)

            deliver_message(mismatching_event_1.id)
            deliver_message(mismatching_event_2.id)
            deliver_message(mismatching_event_3.id)

        self.assertEqual(len(m.request_history), 3)

        self.assertEqual(m.last_request.url, subscription.sink)

        first_request = m.request_history[0]

        self.assertEqual(
            first_request.json(), {**data, "subscription": str(subscription.uuid)}
        )

        second_request = m.request_history[1]

        self.assertEqual(
            second_request.json(),
            {
                **data,
                "subscription": str(subscription.uuid),
                "type": "nl.vng.zaken.zaak_geopend",
            },
        )
        third_request = m.request_history[2]

        self.assertEqual(
            third_request.json(),
            {
                **data,
                "subscription": str(subscription.uuid),
                "type": "nl.vng.burgerzaken.kind_geboren_aangifte_elders",
                "vertrouwelijk": "normaal",
                "domain": "nl.vng.burgerzaken",
            },
        )

    def test_simple_not_filter(self):
        domain = DomainFactory(name="nl.vng.zaken")

        subscription = SubscriptionFactory.create(
            sink="https://vng.zaken.nl/callback",
            filters=[
                {
                    "not": {
                        "exact": {
                            "type": "nl.vng.burgerzaken.kind_geboren_aangifte_elders",
                        },
                    },
                },
            ],
            domain=None,
            source=None,
        )

        data = {
            "id": str(uuid4()),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.zaak_gesloten",
            "data": {"foo": "bar", "bar": "foo"},
        }

        matching_event = EventFactory.create(forwarded_msg=data, domain=domain)
        mismatching_event = EventFactory.create(
            forwarded_msg={
                **data,
                "type": "nl.vng.burgerzaken.kind_geboren_aangifte_elders",
            },
            domain=domain,
        )

        with requests_mock.mock() as m:
            m.post(subscription.sink)

            deliver_message(matching_event.id)
            deliver_message(mismatching_event.id)

        self.assertEqual(len(m.request_history), 1)

        self.assertEqual(m.last_request.url, subscription.sink)
        self.assertEqual(
            m.last_request.json(), {**data, "subscription": str(subscription.uuid)}
        )

    def test_simple_nested_not_filter(self):
        domain = DomainFactory(name="nl.vng.burgerzaken")

        subscription = SubscriptionFactory.create(
            sink="https://vng.zaken.nl/callback",
            filters=[
                {
                    "not": {
                        "not": {
                            "exact": {
                                "type": "nl.vng.burgerzaken.kind_geboren_aangifte_elders",
                            },
                        },
                    },
                },
            ],
            domain=None,
            source=None,
        )

        data = {
            "id": str(uuid4()),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.burgerzaken",
            "type": "nl.vng.burgerzaken.kind_geboren_aangifte_elders",
            "data": {"foo": "bar", "bar": "foo"},
        }

        matching_event = EventFactory.create(forwarded_msg=data, domain=domain)
        mismatching_event = EventFactory.create(
            forwarded_msg={**data, "type": "nl.vng.zaken.zaak_gesloten"}, domain=domain
        )

        with requests_mock.mock() as m:
            m.post(subscription.sink)

            deliver_message(matching_event.id)
            deliver_message(mismatching_event.id)

        self.assertEqual(len(m.request_history), 1)

        self.assertEqual(m.last_request.url, subscription.sink)
        self.assertEqual(
            m.last_request.json(), {**data, "subscription": str(subscription.uuid)}
        )

    def test_complex_nested_not_any(self):
        domain = DomainFactory(name="nl.vng.burgerzaken")

        subscription = SubscriptionFactory.create(
            sink="https://vng.zaken.nl/callback",
            filters=[
                {
                    "not": {
                        "any": [
                            {
                                "exact": {
                                    "type": "nl.vng.burgerzaken.kind_geboren_aangifte_elders",
                                },
                            },
                            {
                                "exact": {
                                    "type": "nl.vng.burgerzaken.persoon_overleden_aangifte_elders",
                                },
                            },
                        ],
                    },
                },
            ],
            domain=None,
            source=None,
        )

        data = {
            "id": str(uuid4()),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.burgerzaken",
            "type": "nl.vng.burgerzaken.persoon_overleden",
            "data": {"foo": "bar", "bar": "foo"},
        }

        matching_event = EventFactory.create(forwarded_msg=data, domain=domain)
        mismatching_event = EventFactory.create(
            forwarded_msg={
                **data,
                "type": "nl.vng.burgerzaken.persoon_overleden_aangifte_elders",
            },
            domain=domain,
        )

        with requests_mock.mock() as m:
            m.post(subscription.sink)

            deliver_message(matching_event.id)
            deliver_message(mismatching_event.id)

        self.assertEqual(len(m.request_history), 1)

        self.assertEqual(m.last_request.url, subscription.sink)
        self.assertEqual(
            m.last_request.json(), {**data, "subscription": str(subscription.uuid)}
        )

    def test_complex_nested_not_all(self):
        domain = DomainFactory(name="nl.vng.burgerzaken")

        subscription = SubscriptionFactory.create(
            sink="https://vng.zaken.nl/callback",
            filters=[
                {
                    "not": {
                        "all": [
                            {
                                "exact": {
                                    "type": "nl.vng.burgerzaken.kind_geboren_aangifte_elders",
                                },
                            },
                            {
                                "exact": {
                                    "type": "nl.vng.burgerzaken.persoon_overleden_aangifte_elders",
                                },
                            },
                        ],
                    },
                },
            ],
            domain=None,
            source=None,
        )

        data = {
            "id": str(uuid4()),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.burgerzaken",
            "type": "nl.vng.burgerzaken.persoon_overleden",
            "data": {"foo": "bar", "bar": "foo"},
        }

        matching_event_1 = EventFactory.create(forwarded_msg=data, domain=domain)
        matching_event_2 = EventFactory.create(
            forwarded_msg={
                **data,
                "type": "nl.vng.burgerzaken.persoon_overleden_aangifte_elders",
            },
            domain=domain,
        )

        with requests_mock.mock() as m:
            m.post(subscription.sink)

            deliver_message(matching_event_1.id)
            deliver_message(matching_event_2.id)

        self.assertEqual(len(m.request_history), 2)

        first_request = m.request_history[0]

        self.assertEqual(first_request.url, subscription.sink)
        self.assertEqual(
            first_request.json(), {**data, "subscription": str(subscription.uuid)}
        )

        second_request = m.request_history[1]

        self.assertEqual(second_request.url, subscription.sink)
        self.assertEqual(
            second_request.json(),
            {
                **data,
                "subscription": str(subscription.uuid),
                "type": "nl.vng.burgerzaken.persoon_overleden_aangifte_elders",
            },
        )

    def test_simple_prefix_filter(self):
        domain = DomainFactory(name="nl.vng.zaken")

        subscription = SubscriptionFactory.create(
            sink="https://vng.zaken.nl/callback",
            filters=[
                {
                    "prefix": {
                        "domain": "nl",
                    },
                },
                {
                    "prefix": {
                        "type": "nl",
                    },
                },
            ],
            domain=None,
            source=None,
        )

        data = {
            "id": str(uuid4()),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.zaak_gesloten",
            "data": {"foo": "bar", "bar": "foo"},
        }

        matching_event = EventFactory.create(forwarded_msg=data, domain=domain)
        mismatching_event = EventFactory.create(
            forwarded_msg={**data, "type": "en.vng.zaken.zaak_geopend"}, domain=domain
        )

        with requests_mock.mock() as m:
            m.post(subscription.sink)

            deliver_message(matching_event.id)
            deliver_message(mismatching_event.id)

        self.assertEqual(len(m.request_history), 1)

        self.assertEqual(m.last_request.url, subscription.sink)
        self.assertEqual(
            m.last_request.json(), {**data, "subscription": str(subscription.uuid)}
        )

    def test_simple_suffix_filter(self):
        domain = DomainFactory(name="nl.vng.zaken")

        subscription = SubscriptionFactory.create(
            sink="https://vng.zaken.nl/callback",
            filters=[
                {
                    "suffix": {
                        "domain": "zaken",
                    },
                },
                {
                    "suffix": {
                        "type": "zaak_gesloten",
                    },
                },
            ],
            domain=None,
            source=None,
        )

        data = {
            "id": str(uuid4()),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.zaak_gesloten",
            "data": {"foo": "bar", "bar": "foo"},
        }

        matching_event = EventFactory.create(forwarded_msg=data, domain=domain)
        mismatching_event = EventFactory.create(
            forwarded_msg={**data, "type": "nl.vng.zaken.zaak_geopend"}, domain=domain
        )

        with requests_mock.mock() as m:
            m.post(subscription.sink)

            deliver_message(matching_event.id)
            deliver_message(mismatching_event.id)

        self.assertEqual(len(m.request_history), 1)

        self.assertEqual(m.last_request.url, subscription.sink)
        self.assertEqual(
            m.last_request.json(), {**data, "subscription": str(subscription.uuid)}
        )

    def test_impossible_all_filter(self):
        """
        Test a filter which could never match an event.
        """
        domain = DomainFactory(name="nl.vng.zaken")

        subscription = SubscriptionFactory.create(
            sink="https://vng.zaken.nl/callback",
            filters=[
                {
                    "all": [
                        {
                            "exact": {
                                "domain": "nl.vng.zaken",
                            },
                        },
                    ]
                },
                {
                    "all": [
                        {
                            "exact": {
                                "domain": "nl.vng.documenten",
                            },
                        },
                    ]
                },
            ],
            domain=None,
            source=None,
        )

        data = {
            "id": str(uuid4()),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.zaak_gesloten",
            "data": {"foo": "bar", "bar": "foo"},
        }

        event_1 = EventFactory.create(forwarded_msg=data, domain=domain)
        event_2 = EventFactory.create(
            forwarded_msg={**data, "domain": "nl.vng.zaken.documenten"}, domain=domain
        )

        with requests_mock.mock() as m:
            m.post(subscription.sink)

            deliver_message(event_1.id)
            deliver_message(event_2.id)

        self.assertEqual(len(m.request_history), 0)


class EventCustomFilterCombinationTests(APITestCase):
    """
    Tests which verify the combination of custom subscription filters
    with attributes on the subscription
    """

    def test_simple_all_filter_with_domain(self):
        domain = DomainFactory(name="nl.vng.zaken")

        subscription = SubscriptionFactory.create(
            sink="https://vng.zaken.nl/callback",
            filters=[
                {
                    "exact": {
                        "type": "nl.vng.zaken.zaak_gesloten",
                    },
                },
                {
                    "suffix": {
                        "source": "Zaaksysteem",
                    },
                },
            ],
            domain=domain,
            source=None,
        )

        data = {
            "id": str(uuid4()),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.zaak_gesloten",
            "data": {"foo": "bar", "bar": "foo"},
        }

        matching_event = EventFactory.create(forwarded_msg=data, domain=domain)
        mismatching_event = EventFactory.create(
            forwarded_msg={
                **data,
                "source": "urn:nld:oin:00000001234567890000:systeem:client",
            },
            domain=domain,
        )

        with requests_mock.mock() as m:
            m.post(subscription.sink)

            deliver_message(matching_event.id)
            deliver_message(mismatching_event.id)

        self.assertEqual(len(m.request_history), 1)

        self.assertEqual(m.last_request.url, subscription.sink)
        self.assertEqual(
            m.last_request.json(), {**data, "subscription": str(subscription.uuid)}
        )

    def test_simple_any_filter_with_source(self):
        domain = DomainFactory(name="nl.vng.zaken")

        subscription = SubscriptionFactory.create(
            sink="https://vng.zaken.nl/callback",
            filters=[
                {
                    "exact": {
                        "type": "nl.vng.zaken.zaak_gesloten",
                    },
                },
                {
                    "any": [
                        {
                            "suffix": {
                                "domain": "zaken",
                            },
                        },
                        {
                            "prefix": {
                                "domain": "zaken",
                            },
                        },
                    ]
                },
            ],
            domain=None,
            source="urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
        )

        data = {
            "id": str(uuid4()),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.zaak_gesloten",
            "data": {"foo": "bar", "bar": "foo"},
        }

        matching_event = EventFactory.create(forwarded_msg=data, domain=domain)
        mismatching_event = EventFactory.create(
            forwarded_msg={
                **data,
                "source": "urn:nld:oin:00000001234567890000:systeem:client",
            },
            domain=domain,
        )

        with requests_mock.mock() as m:
            m.post(subscription.sink)

            deliver_message(matching_event.id)
            deliver_message(mismatching_event.id)

        self.assertEqual(len(m.request_history), 1)

        self.assertEqual(m.last_request.url, subscription.sink)
        self.assertEqual(
            m.last_request.json(), {**data, "subscription": str(subscription.uuid)}
        )

    def test_all_filter_with_coupled_domain(self):
        domain = DomainFactory(name="nl.vng.zaken")
        other_domain = DomainFactory(name="nl.vng.burgerzaken")

        subscription = SubscriptionFactory.create(
            sink="https://vng.zaken.nl/callback",
            filters=[
                {
                    "any": [
                        {
                            "all": [
                                {
                                    "exact": {
                                        "domain": "nl.vng.zaken",
                                    }
                                },
                                {
                                    "any": [
                                        {
                                            "exact": {
                                                "type": "nl.vng.zaken.zaak_gesloten",
                                            }
                                        },
                                        {
                                            "exact": {
                                                "type": "nl.vng.zaken.zaak_geopend",
                                            }
                                        },
                                    ]
                                },
                            ]
                        },
                        {
                            "all": [
                                {
                                    "exact": {
                                        "domain": "nl.vng.burgerzaken",
                                    }
                                },
                                {
                                    "exact": {
                                        "type": "nl.vng.burgerzaken.kind_geboren_aangifte_elders",
                                    }
                                },
                            ]
                        },
                    ]
                }
            ],
            domain=domain,
            source="urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
        )

        data = {
            "id": str(uuid4()),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.zaak_gesloten",
            "data": {"foo": "bar", "bar": "foo"},
        }

        matching_event = EventFactory.create(forwarded_msg=data, domain=domain)
        mismatching_event = EventFactory.create(
            forwarded_msg={
                **data,
                "domain": "nl.vng.burgerzaken",
                "type": "nl.vng.burgerzaken.kind_geboren_aangifte_elders",
            },
            domain=other_domain,
        )

        with requests_mock.mock() as m:
            m.post(subscription.sink)

            deliver_message(matching_event.id)
            deliver_message(mismatching_event.id)

        self.assertEqual(len(m.request_history), 1)

        self.assertEqual(m.last_request.url, subscription.sink)
        self.assertEqual(
            m.last_request.json(), {**data, "subscription": str(subscription.uuid)}
        )

    def test_suffix_multiple_keys(self):
        domain = DomainFactory(name="nl.vng.zaken")

        subscription = SubscriptionFactory.create(
            sink="https://vng.zaken.nl/callback",
            filters=[
                {
                    "suffix": {
                        "domain": "zaken",
                        "type": "nl.vng.zaken.zaak_gesloten",
                    },
                },
            ],
            domain=None,
            source="urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
        )

        data = {
            "id": str(uuid4()),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.zaak_gesloten",
            "data": {"foo": "bar", "bar": "foo"},
        }

        matching_event = EventFactory.create(forwarded_msg=data, domain=domain)

        mismatching_event = EventFactory.create(
            forwarded_msg={
                **data,
                "type": "nl.vng.zaken.zaak_open",
            },
            domain=domain,
        )

        with requests_mock.mock() as m:
            m.post(subscription.sink)

            deliver_message(matching_event.id)
            deliver_message(mismatching_event.id)

        self.assertEqual(len(m.request_history), 1)

        self.assertEqual(m.last_request.url, subscription.sink)
        self.assertEqual(
            m.last_request.json(), {**data, "subscription": str(subscription.uuid)}
        )

    def test_prefix_multiple_keys(self):
        domain = DomainFactory(name="nl.vng.zaken")

        subscription = SubscriptionFactory.create(
            sink="https://vng.zaken.nl/callback",
            filters=[
                {
                    "prefix": {
                        "domain": "nl",
                        "type": "nl.vng.zaken.zaak_gesloten",
                    },
                },
            ],
            domain=None,
            source="urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
        )

        data = {
            "id": str(uuid4()),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.zaak_gesloten",
            "data": {"foo": "bar", "bar": "foo"},
        }

        matching_event = EventFactory.create(forwarded_msg=data, domain=domain)

        mismatching_event = EventFactory.create(
            forwarded_msg={
                **data,
                "type": "nl.vng.zaken.zaak_open",
            },
            domain=domain,
        )

        with requests_mock.mock() as m:
            m.post(subscription.sink)

            deliver_message(matching_event.id)
            deliver_message(mismatching_event.id)

        self.assertEqual(len(m.request_history), 1)

        self.assertEqual(m.last_request.url, subscription.sink)
        self.assertEqual(
            m.last_request.json(), {**data, "subscription": str(subscription.uuid)}
        )
