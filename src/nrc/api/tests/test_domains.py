from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import JWTAuthMixin, get_operation_url
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

        url = get_operation_url("domain_retrieve", uuid=domain.uuid)
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

        data = response.json()

        self.assertEqual(len(data), 1)
        self.assertEqual(response.data[0]["name"], domain1.name)
        self.assertNotEqual(response.data[0]["name"], domain2.name)

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

    def test_update_domain(self):
        """
        test /domains PUT:
        update existent domain
        """
        domain = DomainFactory.create()
        data = {
            "name": "someupdatedname",
            "documentation_link": "https://example.com/doc",
        }

        domain_update_url = get_operation_url("domain_update", uuid=domain.uuid)
        response = self.client.put(domain_update_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        domain.refresh_from_db()

        self.assertEqual(data["name"], domain.name)
        self.assertEqual(data["documentation_link"], domain.documentation_link)

    def test_update_domain_fails_without_name(self):
        """
        test /domains PUT:
        update existent domain without a name
        name is a required field so a 400 should be returned
        """
        domain = DomainFactory.create()
        data = {"documentation_link": "https://example.com/doc"}

        domain_update_url = get_operation_url("domain_update", uuid=domain.uuid)
        response = self.client.put(domain_update_url, data)

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.data
        )

    def test_partial_update_domain(self):
        """
        test /domains PATCH:
        update existent domain
        """
        domain = DomainFactory.create()
        data = {"documentation_link": "https://example.com/doc"}

        name = domain.name
        domain_update_url = get_operation_url("domain_update", uuid=domain.uuid)
        response = self.client.patch(domain_update_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        domain.refresh_from_db()

        self.assertEqual(name, domain.name)
        self.assertEqual(data["documentation_link"], domain.documentation_link)

    def test_destroy_domain(self):
        """
        test /domains DELETE:
        delete existent domain
        """
        domain = DomainFactory.create()
        domain_delete_url = get_operation_url("domain_destroy", uuid=domain.uuid)

        response = self.client.delete(domain_delete_url)

        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT, response.data
        )

        self.assertEqual(Domain.objects.count(), 0)
