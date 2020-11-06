from django.core.management import call_command
from django.test import TestCase

from vng_api_common.authorizations.models import AuthorizationsConfig
from vng_api_common.constants import ComponentTypes
from vng_api_common.models import APICredential, JWTSecret


class SetupConfigurationTests(TestCase):
    def test_setup_configuration(self):
        ac_root = "https://open-zaak.utrecht.nl/autorisaties/api/v1/"
        municipality = "Utrecht"
        openzaak_to_notif_secret = "12345"
        notif_to_openzaak_secret = "54321"

        call_command(
            "setup_configuration",
            ac_root,
            municipality,
            openzaak_to_notif_secret,
            notif_to_openzaak_secret,
        )

        ac_config = AuthorizationsConfig.get_solo()
        self.assertEqual(ac_config.api_root, ac_root)
        self.assertEqual(ac_config.component, ComponentTypes.nrc)

        api_credential = APICredential.objects.get()
        self.assertEqual(api_credential.api_root, ac_root)
        self.assertEqual(
            api_credential.label,
            f"Open Zaak {municipality}",
        )
        self.assertEqual(
            api_credential.client_id, f"open-notificaties-{municipality.lower()}"
        )
        self.assertEqual(api_credential.secret, notif_to_openzaak_secret)
        self.assertEqual(
            api_credential.user_id, f"open-notificaties-{municipality.lower()}"
        )
        self.assertEqual(
            api_credential.user_representation, f"Open Notificaties {municipality}"
        )

        notif_api_jwtsecret_ac = JWTSecret.objects.get()
        self.assertEqual(
            notif_api_jwtsecret_ac.identifier,
            f"open-zaak-backend-{municipality.lower()}",
        )
        self.assertEqual(notif_api_jwtsecret_ac.secret, openzaak_to_notif_secret)
