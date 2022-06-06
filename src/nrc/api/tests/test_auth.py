"""
Guarantee that the proper authorization machinery is in place.
"""
from unittest.mock import patch
from uuid import uuid4

from django.test.utils import override_settings

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import AuthCheckMixin, JWTAuthMixin, reverse

from nrc.api.choices import SequencetypeChoices
from nrc.datamodel.tests.factories import DomainFactory, SubscriptionFactory

from ..scopes import SCOPE_EVENTS_CONSUMEREN, SCOPE_EVENTS_PUBLICEREN


class EventsScopeForbiddenTests(AuthCheckMixin, APITestCase):
    def test_cannot_create_without_correct_scope(self):
        urls = [
            reverse("subscription-list"),
            reverse("domain-list"),
            reverse("event-list"),
        ]

        for url in urls:
            with self.subTest(url=url):
                self.assertForbidden(url, method="post")

    def test_cannot_read_without_correct_scope(self):
        subscription = SubscriptionFactory.create()
        domain = DomainFactory.create()

        urls = [
            reverse("subscription-list"),
            reverse(subscription),
            reverse("domain-list"),
            reverse("domain-detail", kwargs={"name": domain.name}),
        ]

        for url in urls:
            with self.subTest(url=url):
                self.assertForbidden(url, method="get")


class SubscriptionReadCorrectScopeTests(JWTAuthMixin, APITestCase):
    def test_subscription_list(self):
        SubscriptionFactory.create()
        url = reverse("subscription-list")

        for scope in (
            SCOPE_EVENTS_CONSUMEREN,
            SCOPE_EVENTS_PUBLICEREN,
        ):
            with self.subTest(scope=scope):
                self.autorisatie.scopes = [scope]
                self.autorisatie.save()

                response = self.client.get(url)

                self.assertEqual(response.status_code, status.HTTP_200_OK)

                results = response.data

                self.assertEqual(len(results), 1)

    def test_subscription_retrieve(self):
        subscription = SubscriptionFactory.create()
        url = reverse(subscription)

        for scope in (
            SCOPE_EVENTS_CONSUMEREN,
            SCOPE_EVENTS_PUBLICEREN,
        ):
            with self.subTest(scope=scope):
                self.autorisatie.scopes = [scope]
                self.autorisatie.save()

                response1 = self.client.get(url)

                self.assertEqual(response1.status_code, status.HTTP_200_OK)

    def test_read_superuser(self):
        """
        superuser read everything
        """
        self.applicatie.heeft_alle_autorisaties = True
        self.applicatie.save()

        SubscriptionFactory.create()
        url = reverse("subscription-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        self.assertEqual(len(response_data), 1)


class SubscriptionWriteScopeTests(JWTAuthMixin, APITestCase):
    def test_create_scope_not_ok(self):
        self.autorisatie.scopes = (SCOPE_EVENTS_PUBLICEREN,)
        self.autorisatie.save()
        url = reverse("subscription-list")

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_scope_ok(self):
        self.autorisatie.scopes = (SCOPE_EVENTS_CONSUMEREN,)
        self.autorisatie.save()
        url = reverse("subscription-list")

        response = self.client.post(url)

        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_scope_not_ok(self):
        subscription = SubscriptionFactory.create()
        self.autorisatie.scopes = [SCOPE_EVENTS_PUBLICEREN]
        self.autorisatie.save()
        url = reverse(subscription)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_scope_ok(self):
        subscription = SubscriptionFactory.create()
        self.autorisatie.scopes = (SCOPE_EVENTS_CONSUMEREN,)
        self.autorisatie.save()
        url = reverse(subscription)

        response = self.client.delete(url)

        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_scope_not_ok(self):
        subscription = SubscriptionFactory.create()
        self.autorisatie.scopes = (SCOPE_EVENTS_PUBLICEREN,)
        self.autorisatie.save()
        url = reverse(subscription)

        response = self.client.put(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_scope_ok(self):
        subscription = SubscriptionFactory.create()
        self.autorisatie.scopes = (SCOPE_EVENTS_CONSUMEREN,)
        self.autorisatie.save()
        url = reverse(subscription)

        with requests_mock.mock() as m:
            m.register_uri("POST", subscription.sink, status_code=204)
            response = self.client.put(url, {"sink": subscription.sink})

        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DomainReadScopeTests(JWTAuthMixin, APITestCase):
    def test_domain_list(self):
        DomainFactory.create()
        url = reverse("domain-list")

        for scope in (
            SCOPE_EVENTS_CONSUMEREN,
            SCOPE_EVENTS_PUBLICEREN,
        ):
            with self.subTest(scope=scope):
                self.autorisatie.scopes = [scope]
                self.autorisatie.save()

                response = self.client.get(url)

                self.assertEqual(response.status_code, status.HTTP_200_OK)

                results = response.data

                self.assertEqual(len(results), 1)

    def test_domain_retrieve(self):
        domain = DomainFactory.create()
        url = reverse("domain-detail", kwargs={"name": domain.name})

        for scope in (
            SCOPE_EVENTS_CONSUMEREN,
            SCOPE_EVENTS_CONSUMEREN,
        ):
            with self.subTest(scope=scope):
                self.autorisatie.scopes = [scope]
                self.autorisatie.save()

                response = self.client.get(url)

                self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_read_superuser(self):
        self.applicatie.heeft_alle_autorisaties = True
        self.applicatie.save()

        DomainFactory.create()
        url = reverse("domain-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        self.assertEqual(len(response_data), 1)


class DomainWriteScopeTests(JWTAuthMixin, APITestCase):
    def test_create_scope_not_ok(self):
        self.autorisatie.scopes = (SCOPE_EVENTS_CONSUMEREN,)
        self.autorisatie.save()
        url = reverse("domain-list")

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_scope_ok(self):
        self.autorisatie.scopes = (SCOPE_EVENTS_PUBLICEREN,)
        self.autorisatie.save()
        url = reverse("domain-list")

        response = self.client.post(
            url,
            {
                "name": "domain X",
                "documentation_link": "https://www.example.com",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


@patch("nrc.api.serializers.deliver_message.delay")
@override_settings(
    LINK_FETCHER="vng_api_common.mocks.link_fetcher_200",
    ZDS_CLIENT_CLASS="vng_api_common.mocks.MockClient",
)
class EventsWriteScopeTests(JWTAuthMixin, APITestCase):
    def test_create_scope_not_ok(self, mock_task):
        self.autorisatie.scopes = (SCOPE_EVENTS_CONSUMEREN,)
        self.autorisatie.save()
        url = reverse("event-list")

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_scope_ok(self, mock_task):
        self.autorisatie.scopes = (SCOPE_EVENTS_PUBLICEREN,)
        self.autorisatie.save()

        url = reverse("event-list")

        domain = DomainFactory.create(name="nl.vng.zaken")
        subscription = SubscriptionFactory.create(
            sink="https://example.com/callback",
            domain=domain,
        )

        response = self.client.post(
            url,
            {
                "id": str(uuid4()),
                "specversion": "1.0",
                "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
                "domain": "nl.vng.zaken",
                "type": "nl.vng.zaken.status_gewijzigd",
                "time": "2022-03-16T15:29:30.833664Z",
                "subscription": str(subscription.uuid),
                "datacontenttype": "application/json",
                "dataschema": "https://vng.nl/zgw/zaken/status_gewijzigd_schema.json",
                "sequence": "42",
                "sequencetype": SequencetypeChoices.integer,
                "data": {"foo": "bar", "bar": "foo"},
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
