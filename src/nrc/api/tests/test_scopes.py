from unittest.mock import patch
from uuid import uuid4

from django.test import override_settings

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import JWTAuthMixin, get_operation_url

from nrc.api.choices import SequencetypeChoices
from nrc.datamodel.choices import ProtocolChoices
from nrc.datamodel.tests.factories import DomainFactory, SubscriptionFactory

from ..scopes import (
    SCOPE_DOMAINS_CREATE,
    SCOPE_DOMAINS_READ,
    SCOPE_EVENTS_PUBLISH,
    SCOPE_SUBSCRIPTIONS_CREATE,
    SCOPE_SUBSCRIPTIONS_DELETE,
    SCOPE_SUBSCRIPTIONS_READ,
    SCOPE_SUBSCRIPTIONS_UPDATE,
)


@override_settings(
    LINK_FETCHER="vng_api_common.mocks.link_fetcher_200",
    ZDS_CLIENT_CLASS="vng_api_common.mocks.MockClient",
)
class ScopeSubscriptionsRead(JWTAuthMixin, APITestCase):
    scopes = [SCOPE_SUBSCRIPTIONS_READ]
    source = "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem"
    sink = "https://endpoint.example.com/webhook"
    data = {
        "protocol": ProtocolChoices.HTTP,
        "source": source,
        "sink": sink,
        "types": [
            "Type A",
            "Type B",
        ],
    }

    def test_correct_scope(self):
        """
        test /subscriptions GET:
        retrieve subscription with correct scope SCOPE_SUBSCRIPTIONS_READ
        """
        subscription = SubscriptionFactory.create()

        subscription_url = get_operation_url(
            "subscription_update", uuid=subscription.uuid
        )

        with requests_mock.mock() as m:
            m.register_uri("POST", self.sink, status_code=204)
            response = self.client.get(subscription_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

    def test_incorrect_scope(self):
        """
        test /subscriptions POST:
        create subscription with incorrect scope SCOPE_SUBSCRIPTIONS_READ
        """
        subscription_create_url = get_operation_url("subscription_create")

        with requests_mock.mock() as m:
            m.register_uri(
                "POST",
                self.sink,
                status_code=204,
            )
            response = self.client.post(subscription_create_url, self.data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)


@override_settings(
    LINK_FETCHER="vng_api_common.mocks.link_fetcher_200",
    ZDS_CLIENT_CLASS="vng_api_common.mocks.MockClient",
)
class ScopeDomainsRead(JWTAuthMixin, APITestCase):
    scopes = [SCOPE_DOMAINS_READ]

    def test_correct_scope(self):
        """
        test /domains GET:
        retrieve domain with correct scope SCOPE_DOMAINS_READ
        """
        domain = DomainFactory()

        url = get_operation_url("domain_read", uuid=domain.uuid)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_incorrect_scope(self):
        """
        test /domains POST:
        retrieve domain with incorrect scope SCOPE_DOMAINS_READ
        """
        data = {"name": "zaken", "documentation_link": "https://example.com/doc"}

        domain_create_url = get_operation_url("domain_create")
        response = self.client.post(domain_create_url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)


@patch("nrc.api.serializers.deliver_message.delay")
@override_settings(
    LINK_FETCHER="vng_api_common.mocks.link_fetcher_200",
    ZDS_CLIENT_CLASS="vng_api_common.mocks.MockClient",
)
class ScopeEventsCreate(JWTAuthMixin, APITestCase):
    scopes = [SCOPE_EVENTS_PUBLISH]

    def test_correct_scope(self, mocked_task):
        """
        test /events POST:
        create event with correct scope SCOPE_EVENTS_PUBLISH
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


@override_settings(
    LINK_FETCHER="vng_api_common.mocks.link_fetcher_200",
    ZDS_CLIENT_CLASS="vng_api_common.mocks.MockClient",
)
class ScopeSubscriptionsCreate(JWTAuthMixin, APITestCase):
    scopes = [SCOPE_SUBSCRIPTIONS_CREATE]
    source = "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem"
    sink = "https://endpoint.example.com/webhook"
    data = {
        "protocol": ProtocolChoices.HTTP,
        "source": source,
        "sink": sink,
        "types": [
            "Type A",
            "Type B",
        ],
    }

    def test_correct_scope(self):
        """
        test /subscriptions POST:
        create subscription with correct scope SCOPE_SUBSCRIPTIONS_CREATE
        """
        subscription_url = get_operation_url("subscription_create")

        with requests_mock.mock() as m:
            m.register_uri(
                "POST",
                self.sink,
                status_code=204,
            )
            response = self.client.post(subscription_url, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_incorrect_scope(self):
        """
        test /subscriptions PUT:
        update subscription with incorrect scope SCOPE_SUBSCRIPTIONS_CREATE
        """
        subscription = SubscriptionFactory.create()

        subscription_url = get_operation_url(
            "subscription_update", uuid=subscription.uuid
        )

        with requests_mock.mock() as m:
            m.register_uri("POST", self.sink, status_code=204)
            response = self.client.put(subscription_url, self.data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)


@override_settings(
    LINK_FETCHER="vng_api_common.mocks.link_fetcher_200",
    ZDS_CLIENT_CLASS="vng_api_common.mocks.MockClient",
)
class ScopeDomainsCreate(JWTAuthMixin, APITestCase):
    scopes = [SCOPE_DOMAINS_CREATE]

    def test_correct_scope(self):
        """
        test /domains POST:
        create domain with correct scope SCOPE_DOMAINS_CREATE
        """
        data = {"name": "zaken", "documentation_link": "https://example.com/doc"}

        domain_create_url = get_operation_url("domain_create")
        response = self.client.post(domain_create_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_incorrect_scope(self):
        """
        test /domains GET:
        read domain with incorrect scope SCOPE_DOMAINS_CREATE
        """
        domain = DomainFactory()

        url = get_operation_url("domain_read", uuid=domain.uuid)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@override_settings(
    LINK_FETCHER="vng_api_common.mocks.link_fetcher_200",
    ZDS_CLIENT_CLASS="vng_api_common.mocks.MockClient",
)
class ScopeSubscriptionsUpdate(JWTAuthMixin, APITestCase):
    scopes = [SCOPE_SUBSCRIPTIONS_UPDATE]
    source = "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem"
    sink = "https://endpoint.example.com/webhook"
    data = {
        "protocol": ProtocolChoices.HTTP,
        "source": source,
        "sink": sink,
        "types": [
            "Type A",
            "Type B",
        ],
    }

    partial_data = {
        "source": source,
        "sink": sink,
    }

    def test_correct_scope_put(self):
        """
        test /subscriptions PUT:
        update subscription with correct scope SCOPE_SUBSCRIPTIONS_UPDATE
        """
        subscription = SubscriptionFactory.create()

        subscription_url = get_operation_url(
            "subscription_update", uuid=subscription.uuid
        )

        with requests_mock.mock() as m:
            m.register_uri("POST", self.sink, status_code=204)
            response = self.client.put(subscription_url, self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

    def test_correct_scope_patch(self):
        """
        test /subscriptions PATCH:
        update subscription with correct scope SCOPE_SUBSCRIPTIONS_UPDATE
        """
        subscription = SubscriptionFactory.create()

        subscription_url = get_operation_url(
            "subscription_update", uuid=subscription.uuid
        )

        with requests_mock.mock() as m:
            m.register_uri("POST", self.sink, status_code=204)
            response = self.client.patch(subscription_url, self.partial_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

    def test_incorrect_scope(self):
        """
        test /subscriptions POST:
        create subscription with incorrect scope SCOPE_SUBSCRIPTIONS_UPDATE
        """
        subscription_url = get_operation_url("subscription_create")

        with requests_mock.mock() as m:
            m.register_uri(
                "POST",
                self.sink,
                status_code=204,
            )
            response = self.client.post(subscription_url, self.data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)


@override_settings(
    LINK_FETCHER="vng_api_common.mocks.link_fetcher_200",
    ZDS_CLIENT_CLASS="vng_api_common.mocks.MockClient",
)
class ScopeSubscriptionsDelete(JWTAuthMixin, APITestCase):
    scopes = [SCOPE_SUBSCRIPTIONS_DELETE]
    source = "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem"
    sink = "https://endpoint.example.com/webhook"
    data = {
        "protocol": ProtocolChoices.HTTP,
        "source": source,
        "sink": sink,
        "types": [
            "Type A",
            "Type B",
        ],
    }

    def test_correct_scope(self):
        """
        test /subscriptions DELETE:
        delete subscription with correct scope SCOPE_SUBSCRIPTIONS_DELETE
        """
        subscription = SubscriptionFactory.create()

        subscription_url = get_operation_url(
            "subscription_update", uuid=subscription.uuid
        )

        with requests_mock.mock() as m:
            m.register_uri("POST", self.sink, status_code=204)
            response = self.client.delete(subscription_url)

        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT, response.data
        )

    def test_incorrect_scope(self):
        """
        test /subscriptions POST:
        create subscription with correct scope SCOPE_SUBSCRIPTIONS_DELETE
        """
        subscription_url = get_operation_url("subscription_create")

        with requests_mock.mock() as m:
            m.register_uri(
                "POST",
                self.sink,
                status_code=204,
            )
            response = self.client.post(subscription_url, self.data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)
