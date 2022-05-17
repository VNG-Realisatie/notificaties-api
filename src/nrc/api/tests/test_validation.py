from base64 import b64encode
from unittest.case import expectedFailure
from unittest.mock import patch
from uuid import uuid4

from django.test import override_settings
from django.utils.translation import gettext as _

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import JWTAuthMixin, get_operation_url, get_validation_errors

from nrc.api.choices import CredentialTypeChoices, SequencetypeChoices
from nrc.datamodel.choices import ProtocolChoices
from nrc.datamodel.models import Event, Subscription
from nrc.datamodel.tests.factories import DomainFactory, SubscriptionFactory


class SubscriptionsValidationTests(JWTAuthMixin, APITestCase):
    heeft_alle_autorisaties = True

    @override_settings(
        LINK_FETCHER="vng_api_common.mocks.link_fetcher_404",
        ZDS_CLIENT_CLASS="vng_api_common.mocks.MockClient",
    )
    def test_create_subscriptions_extra_fields(self):
        DomainFactory.create(name="zaken")
        subscription_create_url = get_operation_url("subscription_create")

        data = {
            "protocol": ProtocolChoices.HTTP,
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "sink": "https://endpoint.example.com/webhook",
            "domain": "zaken",
            "types": [
                "Type A",
                "Type B",
            ],
            "protocolSettings": {
                "headers": {
                    "Authorization": "Bearer super-sekrit-token",
                },
                "method": "POST",
            },
            "sinkCredential": {
                "credentialType": "ACCESSTOKEN",
                "accessToken": "super-sekrit-token",
                "accessTokenExpiresUtc": "2019-08-24T14:15:22Z",
                "accessTokenType": "bearer",
            },
            "config": {
                "property1": "value1",
                "property2": "value2",
            },
        }

        with requests_mock.mock() as m:
            m.register_uri(
                "POST",
                "https://endpoint.example.com/webhook",
                status_code=204,
            )
            response = self.client.post(subscription_create_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        # check parsing to models
        data = response.json()
        subscription = Subscription.objects.get()

        self.assertEqual(
            subscription.protocol_settings,
            {
                "headers": {
                    "Authorization": "bearer super-sekrit-token",
                },
                "method": "POST",
            },
        )

        self.assertEqual(
            subscription.sink_credential,
            {
                "credential_type": "ACCESSTOKEN",
                "access_token": "super-sekrit-token",
                "access_token_expires_utc": "2019-08-24T14:15:22Z",
                "access_token_type": "bearer",
            },
        )

        self.assertEqual(
            subscription.config,
            {
                "property1": "value1",
                "property2": "value2",
            },
        )

    @override_settings(
        LINK_FETCHER="vng_api_common.mocks.link_fetcher_404",
        ZDS_CLIENT_CLASS="vng_api_common.mocks.MockClient",
    )
    def test_invalid_protocol_settings(self):
        DomainFactory.create(name="zaken")

        data = {
            "protocol": ProtocolChoices.HTTP,
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "sink": "https://endpoint.example.com/webhook",
            "domain": "zaken",
            "protocolSettings": {
                "headers": ["foo"],
                "method": "POST",
            },
        }

        subscription_create_url = get_operation_url("subscription_create")

        with requests_mock.mock() as m:
            m.register_uri(
                "POST", "https://endpoint.example.com/webhook", status_code=204
            )
            response = self.client.post(subscription_create_url, data)

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.data
        )

        error = get_validation_errors(response, "protocolSettings.headers")

        self.assertEqual(
            error["reason"],
            _('Verwachtte een dictionary van items, maar kreeg type "list".'),
        )

    @override_settings(
        LINK_FETCHER="vng_api_common.mocks.link_fetcher_404",
        ZDS_CLIENT_CLASS="vng_api_common.mocks.MockClient",
    )
    def test_invalid_sink_credential(self):
        DomainFactory.create(name="zaken")

        data = {
            "protocol": ProtocolChoices.HTTP,
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "sink": "https://endpoint.example.com/webhook",
            "domain": "zaken",
            "sinkCredential": {
                "credentialType": CredentialTypeChoices.accesstoken,
                "accessToken": "super-sekrit-token",
                "accessTokenExpiresUtc": "foobar",
                "accesTokenType": "bearer",
            },
        }

        subscription_create_url = get_operation_url("subscription_create")

        with requests_mock.mock() as m:
            m.register_uri(
                "POST", "https://endpoint.example.com/webhook", status_code=204
            )
            response = self.client.post(subscription_create_url, data)

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.data
        )

        error = get_validation_errors(response, "sinkCredential.accessTokenExpiresUtc")

        self.assertEqual(
            error["reason"],
            _(
                "Datetime heeft een ongeldig formaat, gebruik 1 van de volgende"
                " formaten: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]."
            ),
        )

    @override_settings(
        LINK_FETCHER="vng_api_common.mocks.link_fetcher_404",
        ZDS_CLIENT_CLASS="vng_api_common.mocks.MockClient",
    )
    def test_subscriptions_invalid_sink(self):
        DomainFactory.create(name="nl.vng.zaken")

        subscription_create_url = get_operation_url("subscription_create")

        data = {
            "protocol": ProtocolChoices.HTTP,
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "sink": "https://endpoint.example.com/webhook",
            "domain": "nl.vng.zaken",
        }

        with requests_mock.mock() as m:
            # Let callback url return 201 instead of required 204 when
            # sending a notification
            m.register_uri(
                "POST", "https://endpoint.example.com/webhook", status_code=201
            )
            response = self.client.post(subscription_create_url, data)

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.data
        )

        error = get_validation_errors(response, "nonFieldErrors")
        self.assertEqual(error["code"], "invalid-callback-url")

    @override_settings(
        LINK_FETCHER="vng_api_common.mocks.link_fetcher_404",
        ZDS_CLIENT_CLASS="vng_api_common.mocks.MockClient",
    )
    def test_subscriptions_callback_url_with_protocol_settings(self):
        DomainFactory.create(name="zaken")
        subscription_create_url = get_operation_url("subscription_create")

        data = {
            "protocol": ProtocolChoices.HTTP,
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "sink": "https://endpoint.example.com/webhook",
            "domain": "zaken",
            "protocolSettings": {
                "headers": {
                    "Authorization": "Bearer super-sekrit-token",
                    "X-Custom-Header": "foobar",
                },
                "method": "POST",
            },
        }

        with requests_mock.mock() as m:
            m.register_uri(
                "POST",
                "https://endpoint.example.com/webhook",
                status_code=204,
            )
            self.client.post(subscription_create_url, data)

        self.assertEqual(
            m.last_request.headers["Authorization"], "Bearer super-sekrit-token"
        )

        self.assertEqual(m.last_request.headers["X-Custom-Header"], "foobar")

    @override_settings(
        LINK_FETCHER="vng_api_common.mocks.link_fetcher_404",
        ZDS_CLIENT_CLASS="vng_api_common.mocks.MockClient",
    )
    def test_subscriptions_callback_url_with_sink_credential(self):
        DomainFactory.create(name="zaken")
        subscription_create_url = get_operation_url("subscription_create")

        data = {
            "protocol": ProtocolChoices.HTTP,
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "sink": "https://endpoint.example.com/webhook",
            "domain": "zaken",
            "sinkCredential": {
                "credentialType": CredentialTypeChoices.accesstoken,
                "accessToken": "super-sekrit-token",
                "accessTokenExpiresUtc": "2019-08-24T14:15:22Z",
                "accessTokenType": "bearer",
            },
        }

        with requests_mock.mock() as m:
            m.register_uri(
                "POST",
                "https://endpoint.example.com/webhook",
                status_code=204,
            )
            self.client.post(subscription_create_url, data)

        self.assertEqual(
            m.last_request.headers["Authorization"], "bearer super-sekrit-token"
        )

    @override_settings(
        LINK_FETCHER="vng_api_common.mocks.link_fetcher_404",
        ZDS_CLIENT_CLASS="vng_api_common.mocks.MockClient",
    )
    def test_subscriptions_callback_url_with_sink_credential_protocol_settings(self):
        """
        Test that sink_credential overrides protocol_settings headers attribute.
        """
        DomainFactory.create(name="zaken")
        subscription_create_url = get_operation_url("subscription_create")

        data = {
            "protocol": ProtocolChoices.HTTP,
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "sink": "https://endpoint.example.com/webhook",
            "domain": "zaken",
            "sinkCredential": {
                "credentialType": CredentialTypeChoices.accesstoken,
                "accessToken": "sink-token",
                "accessTokenExpiresUtc": "2019-08-24T14:15:22Z",
                "accessTokenType": "bearer",
            },
            "protocolSettings": {
                "headers": {
                    "Authorization": "Bearer protocol-token",
                    "X-Custom-Header": "foobar",
                },
                "method": "POST",
            },
        }

        with requests_mock.mock() as m:
            m.register_uri(
                "POST",
                "https://endpoint.example.com/webhook",
                status_code=204,
            )
            self.client.post(subscription_create_url, data)

        self.assertEqual(m.last_request.headers["Authorization"], "bearer sink-token")
        self.assertEqual(m.last_request.headers["X-Custom-Header"], "foobar")

    def test_subscriptions_create_nonexistent_domain(self):
        subscription_create_url = get_operation_url("subscription_create")

        data = {
            "protocol": ProtocolChoices.HTTP,
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "sink": "https://endpoint.example.com/webhook",
            "domain": "foobar",
        }

        response = self.client.post(subscription_create_url, data)

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.data
        )

        error = get_validation_errors(response, "domain")

        self.assertEqual(error["reason"], "Object met name=foobar bestaat niet.")


class DomainsValidationTests(JWTAuthMixin, APITestCase):
    heeft_alle_autorisaties = True

    @override_settings(
        LINK_FETCHER="vng_api_common.mocks.link_fetcher_404",
        ZDS_CLIENT_CLASS="vng_api_common.mocks.MockClient",
    )
    def test_domains_invalid_documentatie_link_url(self):
        domain_create_url = get_operation_url("domain_create")

        data = {
            "name": "nl.vng.zaken",
            "documentation_link": "https://some-bad-url.com/",
        }

        response = self.client.post(domain_create_url, data)

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.data
        )

        error = get_validation_errors(response, "documentationLink")
        self.assertEqual(error["code"], "bad-url")


@patch("nrc.api.serializers.deliver_message.delay")
class EventsValidationTests(JWTAuthMixin, APITestCase):
    heeft_alle_autorisaties = True

    def test_required_fields(self, mock_task):
        event_url = get_operation_url("events_create")

        data = {
            "time": "2022-03-16T15:29:30.833664Z",
            "data": {"foo": "bar", "bar": "foo"},
        }

        response = self.client.post(event_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        for field in (
            "id",
            "specversion",
            "source",
            "type",
        ):
            error = get_validation_errors(response, field)

            with self.subTest(field=field):
                self.assertEqual(error["code"], "required")

    def test_extra_fields(self, mock_task):
        """
        The client application should be able to add custom attributes prefixed
        with the domain name.
        """
        uuid = uuid4()
        subscription_uuid = uuid4()

        SubscriptionFactory.create(domain__name="nl.vng.zaken", uuid=subscription_uuid)

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
            "data": {
                "foo": "bar",
                "bar": "foo",
            },
            "nl.vng.zaken.foo": "bar",
            "nl.vng.zaken.bar": "foo",
            "unknown_attribute": "oops",
        }

        event_url = get_operation_url("events_create")

        response = self.client.post(event_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        event = Event.objects.get()

        self.assertEqual(event.forwarded_msg["nl.vng.zaken.foo"], "bar")
        self.assertEqual(event.forwarded_msg["nl.vng.zaken.bar"], "foo")

        self.assertNotIn("unknown_attribute", event.forwarded_msg)

    def test_extra_fields_other_domain(self, mock_task):
        """
        The client application should not be able to add custom attributes prefixed
        with a domain name which does match with the domain name from the domain attribute.
        """
        uuid = uuid4()
        subscription_uuid = uuid4()

        SubscriptionFactory.create(domain__name="nl.vng.zaken", uuid=subscription_uuid)

        SubscriptionFactory.create(domain__name="nl.vng.documenten", uuid=uuid4())

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
            "data": {
                "foo": "bar",
                "bar": "foo",
            },
            "nl.vng.documenten.foo": "bar",
            "nl.vng.zaken.bar": "foo",
            "unknown_attribute": "oops",
        }

        event_url = get_operation_url("events_create")

        response = self.client.post(event_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        event = Event.objects.get()

        self.assertNotIn("nl.vng.documenten.foo", event.forwarded_msg)
        self.assertNotIn("unknown_attribute", event.forwarded_msg)
        self.assertEqual(event.forwarded_msg["nl.vng.zaken.bar"], "foo")

    def test_unknown_subscription(self, mock_task):
        DomainFactory.create(name="nl.vng.zaken")

        uuid = uuid4()
        subscription_uuid = uuid4()

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

        event_url = get_operation_url("events_create")

        response = self.client.post(event_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "subscription")

        self.assertEqual(error["reason"], _("Subscription bestaat niet."))

    def test_unknown_domain(self, mock_task):
        uuid = uuid4()
        subscription_uuid = uuid4()

        SubscriptionFactory.create(domain__name="nl.vng.zaken")

        data = {
            "id": str(uuid),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.documenten",
            "type": "nl.vng.zaken.status_gewijzigd",
            "time": "2022-03-16T15:29:30.833664Z",
            "subscription": str(subscription_uuid),
            "datacontenttype": "application/json",
            "dataschema": "https://vng.nl/zgw/zaken/status_gewijzigd_schema.json",
            "sequence": "42",
            "sequencetype": SequencetypeChoices.integer,
            "data": {"foo": "bar", "bar": "foo"},
        }

        event_url = get_operation_url("events_create")

        response = self.client.post(event_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "domain")

        self.assertEqual(error["reason"], _("Domain bestaat niet."))

    def test_base64(self, mock_task):
        uuid = uuid4()
        subscription_uuid = uuid4()

        SubscriptionFactory.create(domain__name="nl.vng.zaken", uuid=subscription_uuid)

        base64_data = b64encode(b"Some base64 encoded data")

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
            "data_base64": base64_data.decode("ascii"),
        }

        event_url = get_operation_url("events_create")

        response = self.client.post(event_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        event = Event.objects.get()

        self.assertEqual(
            event.forwarded_msg["data_base64"], base64_data.decode("ascii")
        )

    # TODO: this should return an DSO compliant error response
    @expectedFailure
    def test_invalid_base64(self, mock_task):
        uuid = uuid4()
        subscription_uuid = uuid4()

        SubscriptionFactory.create(domain__name="nl.vng.zaken", uuid=subscription_uuid)

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
            "data_base64": "foobar",
        }

        event_url = get_operation_url("events_create")

        response = self.client.post(event_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "data_base64")

        self.assertEqual(
            error["reason"], _("De opgegeven waarde is geen valide base64.")
        )

    def test_data_or_base64(self, mock_task):
        """
        Events may not contain the data_base64 attribute and the data attribute.
        """
        uuid = uuid4()
        subscription_uuid = uuid4()

        SubscriptionFactory.create(domain__name="nl.vng.zaken", uuid=subscription_uuid)

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
        }

        event_url = get_operation_url("events_create")

        response = self.client.post(event_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "nonFieldErrors")

        self.assertEqual(
            error["reason"], _("Data of data_base64 dient aanwezig te zijn.")
        )

    def test_datacontenttype_validation(self, mock_task):
        """
        For now the API should only accept application/json. Other values should
        not be allowed
        """
        uuid = uuid4()
        subscription_uuid = uuid4()

        SubscriptionFactory.create(domain__name="nl.vng.zaken", uuid=subscription_uuid)

        data = {
            "id": str(uuid),
            "specversion": "1.0",
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "type": "nl.vng.zaken.status_gewijzigd",
            "time": "2022-03-16T15:29:30.833664Z",
            "subscription": str(subscription_uuid),
            "datacontenttype": "application/png",
            "dataschema": "https://vng.nl/zgw/zaken/status_gewijzigd_schema.json",
            "sequence": "42",
            "sequencetype": SequencetypeChoices.integer,
            "data": {
                "foo": "bar",
                "bar": "foo",
            },
        }

        event_url = get_operation_url("events_create")

        response = self.client.post(event_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "datacontenttype")

        self.assertEqual(error["reason"], _("Data contenttype wordt niet ondersteund."))

    def test_data_data_base64_validation(self, mock_task):
        """
        Events may not contain the data_base64 attribute and the data attribute.
        """
        uuid = uuid4()
        subscription_uuid = uuid4()

        SubscriptionFactory.create(domain__name="nl.vng.zaken", uuid=subscription_uuid)

        base64_data = b64encode(b"Some base64 encoded data")

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
            "data_base64": base64_data.decode("ascii"),
            "data": {
                "foo": "bar",
                "bar": "foo",
            },
        }

        event_url = get_operation_url("events_create")

        response = self.client.post(event_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "nonFieldErrors")

        self.assertEqual(
            error["reason"],
            _("Data en data_base64 in combinatie met elkaar zijn niet toegestaan."),
        )
