import uuid as _uuid

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import JSONField
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django_better_admin_arrayfield.models.fields import ArrayField

from nrc.datamodel.choices import ProtocolChoices


class Timestamped(models.Model):
    created_on = models.DateTimeField(_("Aanmaakdatum"), default=timezone.now)
    last_updated = models.DateTimeField(_("Laatst bewerkt"), auto_now=True)

    class Meta:
        abstract = True


# TODO: add filtering
class Domain(Timestamped):
    uuid = models.UUIDField(
        unique=True,
        default=_uuid.uuid4,
        help_text=_("Unique resource identifier (UUID4)"),
    )

    name = models.CharField(
        _("Naam"),
        unique=True,
        help_text=_("Naam van het DOMAIN dat de bron vertegenwoordigd."),
        max_length=255,
    )
    documentation_link = models.URLField(
        _("Documentatie link"), blank=True, help_text=_("URL naar documentatie.")
    )

    filter_attributes = ArrayField(
        models.CharField(max_length=255),
        help_text=_("Filtering op EVENTs op basis van opgegeven attributen"),
        default=list,
        blank=True,
    )

    class Meta:
        verbose_name = _("domain")
        verbose_name_plural = _("domains")
        ordering = (
            "-created_on",
            "name",
        )

    def __str__(self) -> str:
        return self.name


class Subscription(Timestamped):
    uuid = models.UUIDField(
        unique=True,
        default=_uuid.uuid4,
        help_text=_("Unique resource identifier (UUID4)"),
    )

    subscriber_reference = models.CharField(
        _("Referentie subscription"),
        max_length=255,
        blank=True,
    )

    protocol = models.CharField(
        help_text=_("Identificatie van het aflever protocol."),
        choices=ProtocolChoices.choices,
        max_length=255,
    )
    protocol_settings = models.JSONField(
        help_text=_("Instellingen voor het aflever protocol."),
        null=True,
        blank=True,
    )

    sink = models.URLField(
        help_text=_(
            "Het address waarnaar NOTIFICATIEs afgeleverd worden via het opgegeven protocol."
        ),
    )

    sink_credential = models.JSONField(
        verbose_name=_("Sink toegangsgegevens"),
        help_text=_("Toegangsgegevens voor het opgegeven address."),
        null=True,
        blank=True,
    )

    config = models.JSONField(
        help_text=_(
            "Implementatie specifieke instellingen gebruikt door de abbonements "
            "manager om voor het vergaren van notificaties."
        ),
        null=True,
        blank=True,
    )

    source = models.CharField(
        help_text=_("Bron van dit abonnement."),
        max_length=255,
    )

    types = ArrayField(
        models.CharField(max_length=255),
        help_text=_("Notificaties types relevant voor afleveren voor dit abonnement."),
        default=list,
        blank=True,
    )

    domain = models.ForeignKey(
        "datamodel.Domain",
        verbose_name=_("Domain"),
        related_name="domains",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("subscription")
        verbose_name_plural = _("subscriptions")
        ordering = ("-created_on",)

    def __str__(self) -> str:
        return f"{self.uuid}"


# Event
class Event(Timestamped):
    forwarded_msg = JSONField(encoder=DjangoJSONEncoder)
    domain = models.ForeignKey("datamodel.Domain", on_delete=models.CASCADE)

    class Meta:
        ordering = ("-created_on",)

    def __str__(self) -> str:
        return f"Event {self.id} ({self.domain})"


# Used for archiving purposes
class EventResponse(Timestamped):
    event = models.ForeignKey("datamodel.Event", on_delete=models.CASCADE)
    subscription = models.ForeignKey("datamodel.Subscription", on_delete=models.CASCADE)
    exception = models.CharField(max_length=1000, blank=True)
    response_status = models.IntegerField(null=True)

    class Meta:
        ordering = (
            "-created_on",
            "-last_updated",
        )

    def __str__(self) -> str:
        return "{} {}".format(self.subscription, self.response_status or self.exception)
