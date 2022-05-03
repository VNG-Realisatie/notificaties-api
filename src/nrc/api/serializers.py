import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from djangorestframework_camel_case.util import camelize
from rest_framework import serializers
from vng_api_common.validators import URLValidator

from nrc.api.tasks import deliver_message
from nrc.datamodel.models import Abonnement, Kanaal, Notificatie

logger = logging.getLogger(__name__)


# TODO
class KanaalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kanaal
        fields = (
            "naam",
            "documentatie_link",
        )
        extra_kwargs = {
            "documentatie_link": {"required": False, "validators": [URLValidator()]},
        }


# TODO
class AbonnementSerializer(serializers.HyperlinkedModelSerializer):
    domain = serializers.CharField(required=False)

    protocol_settings = serializers.DictField(
        allow_empty=True,
        source="protocol_instellingen",
        help_text=_("Instellingen voor het aflever protocol."),
    )

    sink_credential = serializers.DictField(
        allow_empty=True,
        source="sink_toegangs_gegevens",
        help_text=_("Toegangsgegvens voor het opgegeven address."),
    )

    class Meta:
        model = Abonnement
        fields = (
            "protocol",
            "protocol_settings",
            "sink",
            "sink_credential",
            "config",
            "source",
            "domain",
            "types",
        )

    def validate(self, attrs):
        validated_attrs = super().validate(attrs)
        for group_data in validated_attrs.get("filter_groups", []):
            kanaal_data = group_data["kanaal"]

            # check kanaal exists
            try:
                kanaal = Kanaal.objects.get(naam=kanaal_data["naam"])
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    {"naam": _("Kanaal met deze naam bestaat niet.")},
                    code="kanaal_naam",
                )

            # check abonnement filters are consistent with kanaal filters
            abon_filter_names = [f.key for f in group_data["filters"]]
            if not kanaal.match_filter_names(abon_filter_names):
                raise serializers.ValidationError(
                    {
                        "filters": _(
                            "abonnement filters aren't consistent with kanaal filters"
                        )
                    },
                    code="inconsistent-abonnement-filters",
                )

        return validated_attrs

    def _create_kanalen_filters(self, abonnement, validated_data):
        for group_data in validated_data:
            kanaal_data = group_data.pop("kanaal")
            filters = group_data.pop("filters")

            kanaal = Kanaal.objects.get(naam=kanaal_data["naam"])
            filter_group = FilterGroup.objects.create(
                kanaal=kanaal, abonnement=abonnement
            )
            for filter in filters:
                filter.filter_group = filter_group
                filter.save()

    @transaction.atomic
    def create(self, validated_data):
        groups = validated_data.pop("filter_groups")
        abonnement = super().create(validated_data)
        self._create_kanalen_filters(abonnement, groups)
        return abonnement

    @transaction.atomic
    def update(self, instance, validated_data):
        groups = validated_data.pop("filter_groups", [])
        abonnement = super().update(instance, validated_data)

        # in case of update - delete all related kanalen and filters
        # and create them from request data
        abonnement.filter_groups.all().delete()

        self._create_kanalen_filters(abonnement, groups)
        return abonnement


class MessageSerializer(serializers.Serializer):
    id = serializers.UUIDField(help_text=_("UUID van het EVENT."))

    specversion = serializers.CharField(
        help_text=_(
            "De versie van de CloudEvents specificatie welke het EVENT gebruikt."
        ),
    )

    source = serializers.CharField(
        help_text=_("Identificeert de context waarin een EVENT heeft plaatsgevonden."),
    )

    domain = serializers.CharField(
        help_text=_("Naam van het DOMAIN waartoe het EVENT behoort."),
        required=False,
    )

    type = serializers.CharField(
        help_text=_("Beschrijft het type EVENT afkomstig van het specifieke DOMAIN."),
    )

    time = serializers.DateTimeField(
        help_text=_("Beschrijft het type EVENT afkomstig van het specifieke DOMAIN."),
        required=False,
    )

    subscription = serializers.UUIDField(
        help_text=_(
            "De gebeurtenis is naar de API gepost omdat aan de filtercriteria van"
            " deze SUBSCRIPTION is voldaan. De uuid verwijst naar een SUBSCRIPTION op"
            " de bron die deze EVENT heeft gepubliceerd. Het moet worden"
            " doorgegeven wanneer dit EVENT wordt afgeleverd bij SUBSCRIPTIONs."
            " Wanneer een EVENT wordt gedistribueerd naar een SUBSCRIPTION, moet"
            " dit kenmerk worden overschreven (of ingevuld) met de SUBSCRIPTION's"
            " uuid van de abonnee die de levering heeft geactiveerd."
        ),
        required=False,
    )

    # TODO: validate that the data is of the given conttenttype
    datacontenttype = serializers.CharField(
        help_text=_("Content-type van de meegegeven data."),
        required=False,
    )
    dataschema = serializers.URLField(
        help_text=_("Identificeert het schema waarmee de data gevalideerd kan worden."),
        required=False,
    )

    sequence = serializers.CharField(
        help_text=_("Identificeert het schema waarmee de data gevalideerd kan worden."),
        required=False,
    )

    data = serializers.DictField(
        child=serializers.CharField(),
        required=False,
    )

    # TODO: add validator which validates if this actually has a base64 value
    data_base64 = serializers.CharField(
        help_text=_("Identificeert het schema waarmee de data gevalideerd kan worden."),
        required=False,
    )

    dataref = serializers.CharField(
        help_text=_(
            "Een referentie naar een locatie waar de data van het EVENT is opgeslagen."
        ),
        required=False,
    )

    def validate(self, attrs):
        validated_attrs = super().validate(attrs)

        kanaal = validated_attrs.get("domain")
        abonnement = validated_attrs.get("subscription")

        if kanaal:
            # check if exchange exists
            try:
                Kanaal.objects.get(naam=kanaal)
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    {"domain": _("Domain met deze naam bestaat niet.")},
                    code="message_domain",
                )

        if abonnement:
            # check if exchange exists
            try:
                Abonnement.objects.get(naam=abonnement)
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    {"subscription": _("Subscription met deze UUID bestaat niet.")},
                    code="message_subscription",
                )

        # ensure we're still camelCasing
        return camelize(validated_attrs)

    def _send_to_subs(self, msg: dict):
        # define subs

        # creation of the notification
        abonnement = Abonnement.objects.get(uuid=msg["subscription"])
        kanaal = Kanaal.objects.get(naam=msg["domain"])
        notificatie = Notificatie.objects.create(forwarded_msg=msg, kanaal=kanaal)

        # send to subs
        deliver_message.delay(abonnement.id, msg, notificatie.id)

    def create(self, validated_data: dict) -> dict:
        # TODO: send to queue?

        # send to subs
        self._send_to_subs(validated_data)
        return validated_data
