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


class Domain(Timestamped):
    uuid = models.UUIDField(
        unique=True,
        default=_uuid.uuid4,
        help_text=_("UUID of the domain."),
    )

    name = models.CharField(
        _("Naam"),
        unique=True,
        help_text=_("Name of the domain."),
        max_length=255,
    )
    documentation_link = models.URLField(
        _("Documentatie link"),
        blank=True,
        help_text=_(
            "Link to human readable information about the domain and its notifications."
        ),
    )

    filter_attributes = ArrayField(
        models.CharField(max_length=255),
        help_text=_("Filter attributes offered by the domain."),
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
        help_text=_("UUID of the subscription."),
    )

    subscriber_reference = models.CharField(
        help_text=_(
            "Events that are send to the subscriber will contain this reference. "
            "The subscriber can use the reference for internal routing of the event."
        ),
        max_length=255,
        blank=True,
        null=True,
    )

    protocol = models.CharField(
        help_text=_("Identifier of a delivery protocol."),
        choices=ProtocolChoices.choices,
        max_length=255,
    )
    protocol_settings = models.JSONField(null=True, blank=True)

    sink = models.URLField(
        help_text=_(
            "The address to which events shall be delivered using the selected protocol."
        ),
    )

    sink_credential = models.JSONField(null=True, blank=True)

    config = models.JSONField(
        help_text=_(
            "Implementation-specific configuration parameters needed by the subscription "
            "manager for acquiring events."
        ),
        null=True,
        blank=True,
    )

    source = models.CharField(
        help_text=_(
            "Source to which the subscription applies. May be implied by the request address."
        ),
        max_length=255,
        blank=True,
        null=True,
    )

    types = ArrayField(
        models.CharField(max_length=255),
        help_text=_("CloudEvent types eligible to be delivered by this subscription."),
        blank=True,
        null=True,
    )

    domain = models.ForeignKey(
        "datamodel.Domain",
        verbose_name=_("Domain"),
        help_text=_("Domain to which the subscription applies."),
        related_name="domains",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    filters = models.JSONField(
        help_text=_(
            "This filter evaluates to 'true' if all contained filters are 'true'."
        ),
        blank=True,
        default=dict,
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
