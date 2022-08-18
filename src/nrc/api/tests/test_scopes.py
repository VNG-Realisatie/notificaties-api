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
    SCOPE_DOMAINS_DELETE,
    SCOPE_DOMAINS_READ,
    SCOPE_DOMAINS_UPDATE,
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
class ScopeDomainsTestCase(JWTAuthMixin, APITestCase):
    def test_correct_scope_create(self):
        """
        test /domains POST:
        create domain with correct scope SCOPE_DOMAINS_CREATE
        """
        self.autorisatie.scopes = [SCOPE_DOMAINS_CREATE]
        self.autorisatie.save()
        data = {"name": "zaken", "documentation_link": "https://example.com/doc"}

        domain_create_url = get_operation_url("domain_create")
        response = self.client.post(domain_create_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_incorrect_scope_create(self):
        """
        test /domains GET:
        read domain with incorrect scope SCOPE_DOMAINS_READ
        """
        self.autorisatie.scopes = [SCOPE_DOMAINS_READ]
        self.autorisatie.save()
        data = {"name": "zaken", "documentation_link": "https://example.com/doc"}

        domain_create_url = get_operation_url("domain_create")
        response = self.client.post(domain_create_url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_correct_scope_read(self):
        """
        test /domains GET:
        retrieve domain with correct scope SCOPE_DOMAINS_READ
        """
        self.autorisatie.scopes = [SCOPE_DOMAINS_READ]
        self.autorisatie.save()
        domain = DomainFactory()

        url = get_operation_url("domain_read", uuid=domain.uuid)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_incorrect_scope_read(self):
        """
        test /domains GET:
        retrieve domain with incorrect scope SCOPE_DOMAINS_CREATE
        """
        self.autorisatie.scopes = [SCOPE_DOMAINS_CREATE]
        self.autorisatie.save()
        domain = DomainFactory()

        url = get_operation_url("domain_read", uuid=domain.uuid)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_correct_scope_delete(self):
        """
        test /domains DELETE:
        retrieve domain with correct scope SCOPE_DOMAINS_DELETE
        """
        self.autorisatie.scopes = [SCOPE_DOMAINS_DELETE]
        self.autorisatie.save()
        domain = DomainFactory()

        url = get_operation_url("domain_delete", uuid=domain.uuid)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_incorrect_scope_delete(self):
        """
        test /domains GET:
        retrieve domain with incorrect scope SCOPE_DOMAINS_DELETE
        """
        self.autorisatie.scopes = [SCOPE_DOMAINS_DELETE]
        self.autorisatie.save()
        domain = DomainFactory()

        url = get_operation_url("domain_read", uuid=domain.uuid)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_correct_scope_update_put(self):
        """
        test /domains PUT:
        retrieve domain with correct scope SCOPE_DOMAINS_UPDATE
        """
        self.autorisatie.scopes = [SCOPE_DOMAINS_UPDATE]
        self.autorisatie.save()
        domain = DomainFactory()
        data = {
            "name": "someupdatedname",
            "documentation_link": "https://example.com/doc",
        }

        url = get_operation_url("domain_update", uuid=domain.uuid)
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_correct_scope_update_patch(self):
        """
        test /domains PATCH:
        retrieve domain with correct scope SCOPE_DOMAINS_UPDATE
        """
        self.autorisatie.scopes = [SCOPE_DOMAINS_UPDATE]
        self.autorisatie.save()
        domain = DomainFactory()

        data = {
            "documentation_link": "https://example.com/doc",
        }

        url = get_operation_url("domain_update", uuid=domain.uuid)
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_incorrect_scope_update_put(self):
        """
        test /domains GET:
        retrieve domain with incorrect scope SCOPE_DOMAINS_DELETE
        """
        self.autorisatie.scopes = [SCOPE_DOMAINS_DELETE]
        self.autorisatie.save()
        domain = DomainFactory()

        data = {
            "name": "someupdatedname",
            "documentation_link": "https://example.com/doc",
        }

        url = get_operation_url("domain_update", uuid=domain.uuid)
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)


@override_settings(
    LINK_FETCHER="vng_api_common.mocks.link_fetcher_200",
    ZDS_CLIENT_CLASS="vng_api_common.mocks.MockClient",
)
class ScopeSubscriptionsTestCase(JWTAuthMixin, APITestCase):
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

    def test_correct_scope_read(self):
        """
        test /subscriptions GET:
        retrieve subscription with correct scope SCOPE_SUBSCRIPTIONS_READ
        """
        self.autorisatie.scopes = [SCOPE_SUBSCRIPTIONS_READ]
        self.autorisatie.save()
        subscription_url = get_operation_url("subscription_list")

        response = self.client.get(subscription_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

    def test_incorrect_scope_read(self):
        """
        test /subscriptions POST:
        create subscription with incorrect scope SCOPE_SUBSCRIPTIONS_DELETE
        """
        self.autorisatie.scopes = [SCOPE_SUBSCRIPTIONS_DELETE]
        self.autorisatie.save()
        subscription_url = get_operation_url("subscription_list")

        response = self.client.get(subscription_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_correct_scope_create(self):
        """
        test /subscriptions POST:
        create subscription with correct scope SCOPE_SUBSCRIPTIONS_CREATE
        """
        self.autorisatie.scopes = [SCOPE_SUBSCRIPTIONS_CREATE]
        self.autorisatie.save()
        subscription_url = get_operation_url("subscription_create")

        with requests_mock.mock() as m:
            m.register_uri(
                "POST",
                self.sink,
                status_code=204,
            )
            response = self.client.post(subscription_url, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_incorrect_scope_create(self):
        """
        test /subscriptions PUT:
        update subscription with incorrect scope SCOPE_SUBSCRIPTIONS_DELETE
        """
        self.autorisatie.scopes = [SCOPE_SUBSCRIPTIONS_DELETE]
        self.autorisatie.save()
        subscription = SubscriptionFactory.create()

        subscription_url = get_operation_url(
            "subscription_create", uuid=subscription.uuid
        )

        response = self.client.post(subscription_url, self.data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_correct_scope_delete(self):
        """
        test /subscriptions DELETE:
        delete subscription with correct scope SCOPE_SUBSCRIPTIONS_DELETE
        """
        self.autorisatie.scopes = [SCOPE_SUBSCRIPTIONS_DELETE]
        self.autorisatie.save()
        subscription = SubscriptionFactory.create()

        subscription_url = get_operation_url(
            "subscription_delete", uuid=subscription.uuid
        )

        response = self.client.delete(subscription_url)

        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT, response.data
        )

    def test_incorrect_scope_delete(self):
        """
        test /subscriptions POST:
        create subscription with correct scope SCOPE_SUBSCRIPTIONS_CREATE
        """
        self.autorisatie.scopes = [SCOPE_SUBSCRIPTIONS_CREATE]
        self.autorisatie.save()
        subscription = SubscriptionFactory.create()

        subscription_url = get_operation_url(
            "subscription_delete", uuid=subscription.uuid
        )

        response = self.client.delete(subscription_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_correct_scope_update(self):
        """
        test /subscriptions PUT:
        update subscription with correct scope SCOPE_SUBSCRIPTIONS_UPDATE
        """
        self.autorisatie.scopes = [SCOPE_SUBSCRIPTIONS_UPDATE]
        self.autorisatie.save()
        subscription = SubscriptionFactory.create()

        subscription_url = get_operation_url(
            "subscription_update", uuid=subscription.uuid
        )

        with requests_mock.mock() as m:
            m.register_uri("POST", self.sink, status_code=204)
            response = self.client.put(subscription_url, self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

    def test_correct_scope_partial_update(self):
        """
        test /subscriptions PATCH:
        update subscription with correct scope SCOPE_SUBSCRIPTIONS_UPDATE
        """
        self.autorisatie.scopes = [SCOPE_SUBSCRIPTIONS_UPDATE]
        self.autorisatie.save()
        subscription = SubscriptionFactory.create()

        subscription_url = get_operation_url(
            "subscription_update", uuid=subscription.uuid
        )

        with requests_mock.mock() as m:
            m.register_uri("POST", self.sink, status_code=204)
            response = self.client.patch(subscription_url, self.partial_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

    def test_incorrect_scope_update(self):
        """
        test /subscriptions POST:
        create subscription with incorrect scope SCOPE_SUBSCRIPTIONS_CREATE
        """
        self.autorisatie.scopes = [SCOPE_SUBSCRIPTIONS_CREATE]
        self.autorisatie.save()
        subscription = SubscriptionFactory.create()

        subscription_url = get_operation_url(
            "subscription_update", uuid=subscription.uuid
        )

        response = self.client.put(subscription_url, self.partial_data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_incorrect_scope_partial_update(self):
        """
        test /subscriptions POST:
        create subscription with incorrect scope SCOPE_SUBSCRIPTIONS_CREATE
        """
        self.autorisatie.scopes = [SCOPE_SUBSCRIPTIONS_CREATE]
        self.autorisatie.save()
        subscription = SubscriptionFactory.create()

        subscription_url = get_operation_url(
            "subscription_update", uuid=subscription.uuid
        )

        response = self.client.patch(subscription_url, self.partial_data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)


@patch("nrc.api.serializers.deliver_message.delay")
@override_settings(
    LINK_FETCHER="vng_api_common.mocks.link_fetcher_200",
    ZDS_CLIENT_CLASS="vng_api_common.mocks.MockClient",
)
class ScopeEventsTestcase(JWTAuthMixin, APITestCase):
    def test_correct_scope_publish(self, mocked_task):
        """
        test /events POST:
        create event with correct scope SCOPE_EVENTS_PUBLISH
        """
        self.autorisatie.scopes = [SCOPE_EVENTS_PUBLISH]
        self.autorisatie.save()
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

    def test_incorrect_scope_publish(self, mocked_task):
        """
        test /events POST:
        create event with incorrect scope SCOPE_SUBSCRIPTIONS_CREATE
        """
        self.autorisatie.scopes = [SCOPE_SUBSCRIPTIONS_CREATE]
        self.autorisatie.save()
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

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)
