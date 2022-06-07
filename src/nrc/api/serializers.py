from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from vng_api_common.validators import URLValidator

from nrc.api.choices import (
    AccessTokenTypeChoices,
    CredentialTypeChoices,
    ProtocolMethodChoices,
    SequencetypeChoices,
    SpecVersionChoices,
)
from nrc.api.tasks import deliver_message
from nrc.api.validators import Base64Validator, CallbackURLValidator
from nrc.datamodel.models import Domain, Event, Subscription


class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ("name", "documentation_link", "filter_attributes", "url")

        extra_kwargs = {
            "documentation_link": {"required": False, "validators": [URLValidator()]},
            "url": {"lookup_field": "uuid", "read_only": True},
        }


class ProtocolSettingsSerializer(serializers.Serializer):
    headers = serializers.DictField(
        child=serializers.CharField(max_length=255), required=False
    )

    method = serializers.ChoiceField(
        choices=ProtocolMethodChoices.choices, required=False
    )


class SinkCredentialSerializer(serializers.Serializer):
    credential_type = serializers.ChoiceField(
        choices=CredentialTypeChoices.choices,
    )

    access_token = serializers.CharField()
    access_token_expires_utc = serializers.DateTimeField()
    access_token_type = serializers.ChoiceField(choices=AccessTokenTypeChoices.choices)

    def validate_access_token_expires_utc(self, value):
        field = self.fields["access_token_expires_utc"]
        return field.to_representation(value)


class SubscriptionSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.UUIDField(read_only=True, source="uuid")

    domain = serializers.SlugRelatedField(
        slug_field="name", queryset=Domain.objects.all(), required=False
    )

    protocol_settings = ProtocolSettingsSerializer(required=False)
    sink_credential = SinkCredentialSerializer(required=False)

    class Meta:
        model = Subscription
        fields = (
            "id",
            "protocol",
            "protocol_settings",
            "sink",
            "sink_credential",
            "config",
            "source",
            "domain",
            "types",
        )

        validators = [CallbackURLValidator("sink")]


class EventSerializer(serializers.Serializer):
    id = serializers.CharField(help_text=_("ID van het EVENT."))

    specversion = serializers.ChoiceField(
        help_text=_(
            "De versie van de CloudEvents specificatie welke het EVENT gebruikt."
        ),
        choices=SpecVersionChoices.choices,
    )

    source = serializers.CharField(
        help_text=_("Identificeert de context waarin een EVENT heeft plaatsgevonden."),
    )

    domain = serializers.ModelField(
        help_text=_("Naam van het DOMAIN waartoe het EVENT behoort."),
        model_field=Domain()._meta.get_field("name"),
    )

    type = serializers.CharField(
        help_text=_("Beschrijft het type EVENT afkomstig van het specifieke DOMAIN."),
    )

    time = serializers.DateTimeField(
        help_text=_("Tijdstempel van wanneer het EVENT heeft plaatgevonden."),
        required=False,
    )

    # TODO: implement correct behaviour
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

    datacontenttype = serializers.CharField(
        help_text=_("Content-type van de meegegeven data."),
        required=False,
    )
    dataschema = serializers.URLField(
        help_text=_("Identificeert het schema waarmee de data gevalideerd kan worden."),
        required=False,
    )

    sequence = serializers.CharField(
        help_text=_(
            "Volgorde van het EVENT. Dit maakt het mogelijk meerdere opeenvolgende"
            " EVENTs te versturen."
        ),
        required=False,
    )

    sequencetype = serializers.ChoiceField(
        choices=SequencetypeChoices.choices,
        help_text=_("Specificeert het type van de opgegeven volgorde."),
        required=False,
    )

    subject = serializers.CharField(required=False)

    data = serializers.JSONField(required=False)
    data_base64 = serializers.CharField(validators=[Base64Validator()], required=False)

    dataref = serializers.CharField(
        help_text=_(
            "Een referentie naar een locatie waar de data van het EVENT is opgeslagen."
        ),
        required=False,
    )

    def validate(self, data):
        validated_data = super().validate(data)

        if "data" in validated_data and "data_base64" in validated_data:
            raise ValidationError(
                _("Data en data_base64 in combinatie met elkaar zijn niet toegestaan.")
            )
        elif not "data" in validated_data and not "data_base64" in validated_data:
            raise ValidationError(_("Data of data_base64 dient aanwezig te zijn."))

        combination_fields = {
            "sequencetype",
            "sequence",
        }

        if any(field in validated_data for field in combination_fields) and not all(
            field in validated_data for field in combination_fields
        ):
            found_fields = set(
                field for field in combination_fields if field in validated_data
            )
            missing_fields = combination_fields - found_fields
            raise ValidationError(
                _(
                    "Velden %(missing_fields)s zijn verplicht bij het gebruik van %(found_fields)s."
                )
                % {
                    "missing_fields": ",".join(missing_fields),
                    "found_fields": ",".join(found_fields),
                }
            )

        return validated_data

    def validate_domain(self, value):
        try:
            Domain.objects.get(name=value)
        except Domain.DoesNotExist:
            raise ValidationError(_("Domain bestaat niet."), code="does_not_exist")

        return value

    # TODO: send to queue?
    def create(self, validated_data: dict) -> dict:
        domain = Domain.objects.get(name=self.validated_data["domain"])

        custom_fields = {
            key: value
            for key, value in self.initial_data.items()
            if key not in validated_data
        }

        event = Event.objects.create(
            forwarded_msg={**custom_fields, **validated_data}, domain=domain
        )

        deliver_message.delay(event.id)
        return validated_data
