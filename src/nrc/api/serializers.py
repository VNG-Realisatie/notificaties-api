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
from nrc.api.validators import Base64Validator, CallbackURLValidator, FilterValidator
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
    id = serializers.UUIDField(
        read_only=True,
        source="uuid",
        help_text=_("UUID of the subscription."),
    )

    domain = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Domain.objects.all(),
        required=False,
        allow_null=True,
        help_text=_("Domain to which the subscription applies."),
    )

    protocol_settings = ProtocolSettingsSerializer(required=False, allow_null=True)
    sink_credential = SinkCredentialSerializer(required=False, allow_null=True)

    filters = serializers.JSONField(
        validators=[FilterValidator()],
        required=False,
        help_text=_(
            "This filter evaluates to 'true' if all contained filters are 'true'."
        ),
    )

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
            "subscriber_reference",
            "filters",
        )

        validators = [CallbackURLValidator("sink")]


class EventSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text=_(
            "Identifies the event. Producers MUST ensure that source + id is "
            "unique for each distinct event. SHOULD be a UUID."
        )
    )

    specversion = serializers.ChoiceField(
        help_text=_(
            "The version of the CloudEvents specification which the event uses. "
            "Compliant event producers MUST use a value of 1.0 when referring to "
            "this version of the specification."
        ),
        choices=SpecVersionChoices.choices,
    )

    source = serializers.CharField(
        help_text=_(
            "Identifies the context in which an event happened. SHOULD be a URN "
            "notation with 'nld' as namespace identifier. SHOULD contain consecutive "
            "a unique identifier of the organization that publishes the event followed "
            "by the source system that publishes the event. Involved organizations "
            "SHOULD agree on how organizations and systems are uniquely identified "
            "(e.g. via the use of OIN, KVK-nummer or eIDAS legal identifier for "
            "organization identification);."
        ),
    )

    domain = serializers.ModelField(
        help_text=_(
            "Name of the domain to which the event belongs. Can be seen as the "
            "namespace of the event.(This attribute is not listed in the GOV NL "
            "profile for CloudEvents)."
        ),
        model_field=Domain()._meta.get_field("name"),
    )

    type = serializers.CharField(
        help_text=_(
            "Beschrijft het type EVENT afkomstig van het specifieke DOMAIN."
            "This attribute contains a value describing the type of event. Type "
            "SHOULD start with the domain followed by the name of the event. Events "
            "SHOULD be expressed in the past tense. If subtypes are required those "
            "SHOULD be expressed using a dot '.' between the super and subtype(s). "
            "The type MAY contain version information. Version information SHOULD "
            "be appended at the end of the string."
        ),
    )

    time = serializers.DateTimeField(
        help_text=_(
            "Timestamp of the event. SHOULD be the timestamp the event was registered "
            "in the source system and NOT the time the event occurred in reality. "
            "The exact meaning of time MUST be clearly documented."
        ),
        required=False,
        allow_null=True,
    )

    subscription = serializers.UUIDField(
        help_text=_(
            "Usually empty. Only used in situations where notificationservices are "
            "chained. For example notificationservice2 (ns2) is subscribed to "
            "notifcationservice1 (ns1). When ns1 sends an event to ns2 this attribute "
            "SHOULD contain the subscription id of the subscription that ns1 has "
            "on ns2 (that was resposible for receiving the event). Note this "
            "attribute is overwritten when the event is passed through to a client. "
            "It will be set to the value of the subscription id of the subscription "
            "of the client."
        ),
        required=False,
        allow_null=True,
    )

    # TODO: we should pick either camelcase (like other ZGW components) or allow underscores
    subscriberReference = serializers.CharField(
        help_text=_(
            "Usually empty. Only used in situations where notificationservices are "
            "chained. For example notificationservice2 (ns2) is subscribed to "
            "notifcationservice1 (ns1). When ns1 sends an event to ns2 this attribute "
            "COULD contain the subscriberReference the was specified when ns2 "
            "subscribed to ns1. Note this attribute is overwritten when the event "
            "is passed through to a client. It will be set to the value of the "
            "subscriberReference of the subscription of the client (when specified "
            "by the client)."
        ),
        max_length=255,
        required=False,
        allow_null=True,
    )

    datacontenttype = serializers.CharField(
        help_text=_(
            "Content type of data value. In this version of the API the value MUST "
            "be 'application/json'. In future versions of the API other values "
            "such as described in RFC 2046 MAY be used."
        ),
        required=False,
        allow_null=True,
    )
    dataschema = serializers.URLField(
        help_text=_("Identifies the schema that data adheres to."),
        required=False,
        allow_null=True,
    )

    sequence = serializers.CharField(
        help_text=_(
            "Value expressing the relative order of the event. This enables "
            "interpretation of data supercedence."
        ),
        required=False,
        allow_null=True,
    )

    sequencetype = serializers.ChoiceField(
        choices=SequencetypeChoices.choices,
        help_text=_(
            "Specifies the semantics of the sequence attribute. (Currently limited "
            "to the value INTEGER)."
        ),
        required=False,
        allow_null=True,
    )

    subject = serializers.CharField(
        help_text=_(
            "Included to be compatible with CloudEvents specification. The GOV NL "
            "profile states 'Decision on whether or not to use the attribute and/or "
            "the exact interpretation is postponed. To be determined partly on the "
            "basis of future agreements about subscription and filtering.'"
        ),
        required=False,
        allow_null=True,
    )

    data = serializers.JSONField(required=False, allow_null=True)
    data_base64 = serializers.CharField(
        validators=[Base64Validator()],
        help_text=_(
            "The presence of the data_base64 member clearly indicates that the "
            "value is a Base64 encoded binary data, which the serializer MUST decode "
            "into a binary runtime data type."
        ),
        required=False,
        allow_null=True,
    )

    dataref = serializers.CharField(
        help_text=_(
            "A reference to a location where the event payload is stored. If both "
            "the data attribute and the dataref attribute are specified their "
            "contents MUST be identical."
        ),
        required=False,
        allow_null=True,
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
