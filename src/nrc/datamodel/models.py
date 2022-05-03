
from django.contrib.postgres.fields import ArrayField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import JSONField
from django.utils.translation import ugettext_lazy as _


# Domain
# TODO: add filtering
class Kanaal(models.Model):
    naam = models.CharField(
        _("Naam"),
        unique=True,
        help_text=_("Naam van het KANAAL dat de bron vertegenwoordigd."),
    )
    documentatie_link = models.URLField(
        _("Documentatie link"), blank=True, help_text=_("URL naar documentatie.")
    )

    class Meta:
        verbose_name = _("kanaal")
        verbose_name_plural = _("kanalen")

    def __str__(self) -> str:
        return self.naam


# Subscription
class Abonnement(models.Model):
    protocol = models.CharField(
        help_text=_("Identificatie van het aflever protocol."),
        default="HTTP",  # TODO: create enum?
    )
    protocol_instellingen = models.JSONField(
        help_text=_("Instellingen voor het aflever protocol.")
    )

    sink = models.CharField(
        help_text=_(
            "Het address waarnaar NOTIFICATIEs afgeleverd worden via het opgegeven protocol."
        ),
        blank=True,
    )

    sink_toegangs_gegevens = models.JSONField(
        verbose_name=_("Sink toegangsgegevens"),
        help_text=_("Toegangsgegevens voor het opgegeven address."),
    )

    config = models.JSONField(
        help_text=_(
            "Implementatie specifieke instellingen gebruikt door de abbonements "
            "manager om voor het vergaren van notificaties."
        ),
    )

    source = models.CharField(help_text=_("Bron van dit abonnement."))

    types = ArrayField(
        models.CharField(),
        help_text=_("Notificaties types relevant voor afleveren voor dit abonnement."),
        blank=True,
    )

    kanaal = models.ForeignKey(
        Kanaal,
        verbose_name=_("Kanaal"),
        related_name="abonnementen",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("abonnement")
        verbose_name_plural = _("abonnementen")

    def __str__(self) -> str:
        return f"{self.uuid}"


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
