from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import JWTAuthMixin, get_operation_url,reverse
from vng_api_common.tests.schema import get_validation_errors

from nrc.datamodel.models import Domain
from nrc.datamodel.tests.factories import DomainFactory


@override_settings(
    LINK_FETCHER="vng_api_common.mocks.link_fetcher_200",
    ZDS_CLIENT_CLASS="vng_api_common.mocks.MockClient",
)
class DomainsTestCase(JWTAuthMixin, APITestCase):
    heeft_alle_autorisaties = True

    def test_domain_create(self):
        """
        test /domains POST:
        create domain via POST request
        check if data were parsed to models correctly
        """
        data = {"name": "zaken", "documentation_link": "https://example.com/doc"}

        domain_create_url = get_operation_url("domain_create")
        response = self.client.post(domain_create_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        # check parsing to model
        data = response.json()
        domain = Domain.objects.get()

        self.assertEqual(domain.name, "zaken")
        self.assertEqual(domain.documentation_link, "https://example.com/doc")

    def test_domain_retrieve(self):
        """
        test /domains GET:
        retrieve specified domain
        """
        domain = DomainFactory()

        url = get_operation_url("domain_read", uuid=domain.uuid)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "name": domain.name,
                "documentationLink": domain.documentation_link,
                "filterAttributes": domain.filter_attributes,
                "uuid": str(domain.uuid),
                "url": f"http://testserver{url}",
            },
        )

    def test_domain_create_nonunique(self):
        """
        test /domains POST:
        attempt to create kanaal with the same name as an existent kanaal
        check if response contents status 400
        """
        Domain.objects.create(name="zaken")
        data = {"name": "zaken", "documentation_link": "https://example.com/doc"}

        domain_create_url = get_operation_url("domain_create")
        response = self.client.post(domain_create_url, data)

        validation_error = get_validation_errors(response, "name")

        self.assertEqual(validation_error["code"], "unique")
        self.assertEqual(
            validation_error["reason"], "Er bestaat al een domain met eenzelfde Naam."
        )
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.data
        )

    def test_domain_update_delete(self):
        """
        test /domains PUT, DELETE:
        attempt to update and destroy kanaal via request
        check if response contents status 405
        """
        domain = Domain.objects.create(name="zaken")
        data = {"documentatie_link": "https://example.com/doc"}

        domain_url = get_operation_url("domain_read", uuid=domain.uuid)
        response_put = self.client.put(domain_url, data)

        self.assertEqual(
            response_put.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
            response_put.data,
        )

        response_delete = self.client.delete(domain_url, data)

        self.assertEqual(
            response_delete.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
            response_delete.data,
        )

    def test_domain_filter_naam(self):
        """
        test /domains GET with query param (naam):
        check if filtering via query params is correct
        """
        domain1, domain2 = DomainFactory.create_batch(2)
        assert domain1.name != domain2.name

        list_url = get_operation_url("domain_list")
        response = self.client.get(list_url, {"name": domain1.name})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()['results']

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], domain1.name)
        self.assertNotEqual(data[0]["name"], domain2.name)

    def test_filter_attributes(self):
        data = {
            "name": "zaken",
            "documentation_link": "https://example.com/doc",
            "filter_attributes": [
                "bronorganisatie",
                "vertrouwelijkheid",
            ],
        }

        domain_create_url = get_operation_url("domain_create")
        response = self.client.post(domain_create_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        # check parsing to model
        data = response.json()
        domain = Domain.objects.get()

        self.assertEqual(domain.name, "zaken")
        self.assertEqual(domain.documentation_link, "https://example.com/doc")
        self.assertEqual(
            domain.filter_attributes, ["bronorganisatie", "vertrouwelijkheid"]
        )

class DomainPaginationTestsCase(JWTAuthMixin, APITestCase):
    heeft_alle_autorisaties = True

    def test_pagination_default(self):
        domain1, domain2 = DomainFactory.create_batch(2)
        url = get_operation_url("domain_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data["count"], 2)
        self.assertIsNone(response_data["previous"])
        self.assertIsNone(response_data["next"])

    def test_pagination_page_param(self):
        domain1, domain2 = DomainFactory.create_batch(2)
        url = get_operation_url("domain_list")

        response = self.client.get(url, {"page": 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data["count"], 2)
        self.assertIsNone(response_data["previous"])
        self.assertIsNone(response_data["next"])
