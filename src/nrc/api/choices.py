from django.db.models.enums import TextChoices
from django.utils.translation import gettext_lazy as _


class SpecVersionChoices(TextChoices):
    one = (
        "1.0",
        _("1"),
    )


class SequencetypeChoices(TextChoices):
    integer = ("Integer", _("Integer"))


class ProtocolMethodChoices(TextChoices):
    post = ("POST", _("POST"))


class CredentialTypeChoices(TextChoices):
    accesstoken = ("ACCESSTOKEN", _("Access token"))


class AccessTokenTypeChoices(TextChoices):
    bearer = ("bearer", _("Bearer"))
