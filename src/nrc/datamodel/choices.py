from django.db import models
from django.utils.translation import gettext_lazy as _


class ProtocolChoices(models.TextChoices):
    HTTP = (
        "HTTP",
        _("HTTP"),
    )
