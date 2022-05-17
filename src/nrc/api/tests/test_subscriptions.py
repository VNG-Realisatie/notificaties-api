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
        expected_domain = Domain.objects.get(name="zaken")

        self.assertEqual(Subscription.objects.count(), 1)
        self.assertEqual(Domain.objects.count(), 1)

        self.assertEqual(subscription.domain, expected_domain)
        self.assertEqual(subscription.protocol, ProtocolChoices.HTTP)
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
        existing_domain = DomainFactory.create(name="foo")
        new_domain = DomainFactory.create(name="zaken")

        subscription.domain = existing_domain

        data = {
            "protocol": ProtocolChoices.HTTP,
            "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
            "sink": "https://new.endpoint.example.com/webhook",
            "domain": "zaken",
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

        self.assertEqual(subscription.domain, new_domain)
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

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        data = response.json()

        subscription.refresh_from_db()

        self.assertEqual(subscription.types, ["Type A", "Type B", "Type C"])

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