from uuid import uuid4

from django.test import override_settings

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import JWTAuthMixin, get_operation_url

from nrc.datamodel.choices import ProtocolChoices
from nrc.datamodel.models import Domain, Subscription
from nrc.datamodel.tests.factories import DomainFactory, SubscriptionFactory


@override_settings(
    LINK_FETCHER="vng_api_common.mocks.link_fetcher_200",
    ZDS_CLIENT_CLASS="vng_api_common.mocks.MockClient",
)
class SubscriptionsTestCase(JWTAuthMixin, APITestCase):
    heeft_alle_autorisaties = True

    def test_subscriptions_create(self):
        """
        test /subscriptions POST:
        create subscription with required fields only via POST request
        check if data were parsed to models correctly
        """
        subscription_create_url = get_operation_url("subscription_create")

        data = {
            "protocol": ProtocolChoices.HTTP,
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "sink": "https://endpoint.example.com/webhook",
            "types": [
                "Type A",
                "Type B",
            ],
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

        self.assertEqual(Subscription.objects.count(), 1)

        self.assertEqual(subscription.protocol, ProtocolChoices.HTTP)
        self.assertEqual(
            subscription.sink,
            "https://endpoint.example.com/webhook",
        )
        self.assertEqual(
            subscription.source,
            "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
        )

    def test_subscriptions_create_subscriber_reference(self):
        """
        test /subscriptions POST:
        create subscription with extra field subscriberReference
        """
        subscription_create_url = get_operation_url("subscription_create")
        reference = uuid4()

        data = {
            "protocol": ProtocolChoices.HTTP,
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "sink": "https://endpoint.example.com/webhook",
            "types": [
                "Type A",
                "Type B",
            ],
            "subscriber_reference": str(reference),
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

        self.assertEqual(Subscription.objects.count(), 1)

        self.assertEqual(subscription.subscriber_reference, str(reference))

    def test_subscriptions_domain(self):
        """
        test /subscriptions POST:
        create subscription with extra domain field via POST request
        check if data were parsed to models correctly
        """
        DomainFactory(name="nl.vng.zaken")

        data = {
            "protocol": ProtocolChoices.HTTP,
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "domain": "nl.vng.zaken",
            "sink": "https://endpoint.example.com/webhook",
            "types": [
                "Type A",
                "Type B",
            ],
        }

        subscription_create_url = get_operation_url("subscription_create")

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
        expected_domain = Domain.objects.get(name="nl.vng.zaken")

        self.assertEqual(Subscription.objects.count(), 1)
        self.assertEqual(Domain.objects.count(), 1)

        self.assertEqual(subscription.protocol, ProtocolChoices.HTTP)
        self.assertEqual(subscription.domain, expected_domain)
        self.assertEqual(
            subscription.sink,
            "https://endpoint.example.com/webhook",
        )
        self.assertEqual(
            subscription.source,
            "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
        )

    def test_update_subscriptions(self):
        """
        test /subscriptions PUT:
        update existent subscription
        """
        subscription = SubscriptionFactory.create()

        data = {
            "protocol": ProtocolChoices.HTTP,
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "sink": "https://new.endpoint.example.com/webhook",
            "types": [
                "Type A",
                "Type B",
            ],
        }

        subscription_update_url = get_operation_url(
            "subscription_update", uuid=subscription.uuid
        )

        with requests_mock.mock() as m:
            m.register_uri(
                "POST", "https://new.endpoint.example.com/webhook", status_code=204
            )
            response = self.client.put(subscription_update_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        data = response.json()

        subscription.refresh_from_db()

        self.assertEqual(subscription.sink, "https://new.endpoint.example.com/webhook")

    def test_partial_update_subscriptions(self):
        """
        test /subscriptions PATCH:
        update existent subscription
        """
        subscription = SubscriptionFactory.create(
            sink="https://endpoint.example.com/webhook"
        )

        data = {
            "types": [
                "Type A",
                "Type B",
                "Type C",
            ],
        }

        subscription_update_url = get_operation_url(
            "subscription_update", uuid=subscription.uuid
        )

        with requests_mock.mock() as m:
            m.register_uri(
                "POST", "https://endpoint.example.com/webhook", status_code=204
            )
            response = self.client.patch(subscription_update_url, data)

        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN
        )  # scope check is done before returning 405
        self.assertEqual(subscription.types, None)

    def test_subscription_destroy(self):
        """
        test /subscriptions DELETE:
        check if destroy action is supported
        """
        subscription = SubscriptionFactory.create()
        subscription_url = get_operation_url(
            "subscription_read", uuid=subscription.uuid
        )

        response = self.client.delete(subscription_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Subscription.objects.count(), 0)

    def test_nullable_fields(self):
        """
        test /subscriptions POST:
        create subscription with nullable fields via POST request
        """
        subscription_create_url = get_operation_url("subscription_create")

        data = {
            "protocol": ProtocolChoices.HTTP,
            "sink": "https://endpoint.example.com/webhook",
            "protocol_settings": None,
            "sink_credential": None,
            "source": None,
            "domain": None,
            "config": None,
            "subscriber_reference": None,
            "types": None,
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

        self.assertEqual(Subscription.objects.count(), 1)

        self.assertEqual(subscription.protocol_settings, None)
        self.assertEqual(subscription.sink_credential, None)
        self.assertEqual(subscription.source, None)
        self.assertEqual(subscription.domain, None)
        self.assertEqual(subscription.config, None)
        self.assertEqual(subscription.subscriber_reference, None)
        self.assertEqual(subscription.types, None)

    def test_subscription_custom_filtering_exact_simple(self):
        """
        test /subscriptions POST:
        create subscription with custom filtering
        """
        subscription_create_url = get_operation_url("subscription_create")

        data = {
            "protocol": ProtocolChoices.HTTP,
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "sink": "https://endpoint.example.com/webhook",
            "filters": [
                {
                    "exact": {
                        "attribute": "domain",
                        "value": "nl.vng.zaken",
                    },
                },
                {
                    "exact": {
                        "attribute": "type",
                        "value": "nl.vng.zaken.zaak_gesloten",
                    },
                },
            ],
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

        self.assertEqual(Subscription.objects.count(), 1)

        self.assertEqual(subscription.protocol, ProtocolChoices.HTTP)
        self.assertEqual(subscription.filters, data["filters"])
