from django.test import TestCase

from zds_client.auth import ClientAuth

from notifications.utils.exceptions import AbonnementAuthException

from ..models import Abonnement
from .factories import AbonnementFactory


class AbonnementTests(TestCase):

    def test_get_client_id_success(self):
        """
        Test match_pattern method:
        Assert it if filters in message and in abonnement data match
        """
        auth = ClientAuth(
            client_id='zrc',
            secret='my-secret',
            scopes=['zds.scopes.zaken.aanmaken']
        )
        auth_encoded = auth.credentials()['Authorization']

        abonnment = AbonnementFactory.create(auth=auth_encoded)

        self.assertEqual(abonnment.client_id, 'zrc')

    def test_get_client_id_fail(self):
        self.assertRaises(
            AbonnementAuthException,
            AbonnementFactory.create,
            auth='Bearer 1234')
