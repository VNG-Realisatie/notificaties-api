import uuid as _uuid

from django.contrib.postgres.fields import ArrayField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import JSONField
from django.utils.translation import ugettext_lazy as _


# Domain
class Kanaal(models.Model):
    uuid = models.UUIDField(
        unique=True,
        default=_uuid.uuid4,
        help_text=_("Unique resource identifier (UUID4)"),
    )
    naam = models.CharField(
        _("Naam"),
        max_length=50,
        unique=True,
        help_text=_(
            'Naam van het KANAAL (ook wel "Exchange" genoemd) dat de bron vertegenwoordigd.'
        ),
    )
    documentatie_link = models.URLField(
        _("Documentatie link"), blank=True, help_text=_("URL naar documentatie.")
    )
    filters = ArrayField(
        models.CharField(max_length=100),
        verbose_name=_("filters"),
        blank=True,
        default=list,
        help_text=_(
            "Lijst van mogelijke filter kenmerken van een KANAAL. Deze "
            "filter kenmerken kunnen worden gebruikt bij het aanmaken "
            "van een ABONNEMENT."
        ),
    )

    class Meta:
        verbose_name = _("kanaal")
        verbose_name_plural = _("kanalen")

    def __str__(self) -> str:
        return f"{self.naam}"

    def match_filter_names(self, obj_filters: list) -> bool:
        set_kanaal_filters = set(self.filters)
        set_obj_filters = set(obj_filters)
        if (
            set_kanaal_filters <= set_obj_filters
            or set_kanaal_filters >= set_obj_filters
        ):
            return True
        return False


# Subscription
class Abonnement(models.Model):
    uuid = models.UUIDField(
        unique=True,
        default=_uuid.uuid4,
        help_text=_("Unique resource identifier (UUID4)"),
    )
    callback_url = models.URLField(
        _("Callback URL"),
        unique=True,
        help_text=_(
            "De URL waar notificaties naar toe gestuurd dienen te worden. Deze URL dient uit te komen bij een "
            "API die geschikt is om notificaties op te ontvangen."
        ),
    )
    auth = models.CharField(
        _("Autorisatie header"),
        max_length=1000,
        help_text=_(
            'Autorisatie header invulling voor het vesturen naar de "Callback URL". Voorbeeld: Bearer '
            "a4daa31..."
        ),
    )
    client_id = models.CharField(
        _("Client ID"),
        max_length=100,
        blank=True,
        help_text=_("Client ID extracted from Auth header"),
    )

    class Meta:
        verbose_name = _("abonnement")
        verbose_name_plural = _("abonnementen")

    def __str__(self) -> str:
        return f"{self.uuid}"

    @property
    def kanalen(self):
        return set([f.kanaal for f in self.filter_groups.all()])


# Event
class Notificatie(models.Model):
    forwarded_msg = JSONField(encoder=DjangoJSONEncoder)
    kanaal = models.ForeignKey(Kanaal, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return "Notificatie ({})".format(self.kanaal)


# Used for archiving purposes
class NotificatieResponse(models.Model):
    notificatie = models.ForeignKey(Notificatie, on_delete=models.CASCADE)
    abonnement = models.ForeignKey(Abonnement, on_delete=models.CASCADE)
    exception = models.CharField(max_length=1000, blank=True)
    response_status = models.IntegerField(null=True)

    def __str__(self) -> str:
        return "{} {}".format(self.abonnement, self.response_status or self.exception)
