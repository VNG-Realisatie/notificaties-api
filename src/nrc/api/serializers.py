import json
import logging

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from djangorestframework_camel_case.util import camelize
from rest_framework import fields, serializers
from vng_api_common.notifications.api.serializers import NotificatieSerializer
from vng_api_common.validators import URLValidator

from nrc.api.tasks import deliver_message
from nrc.datamodel.models import (
    Abonnement, Filter, FilterGroup, Kanaal, Notificatie
)

logger = logging.getLogger(__name__)


class FiltersField(fields.DictField):

    def to_representation(self, instance):
        qs = instance.all()
        return dict(qs.values_list('key', 'value'))

    def to_internal_value(self, data):
        return [Filter(key=k, value=v) for k, v in data.items()]


class KanaalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kanaal
        fields = (
            'url',
            'naam',
            'documentatie_link',
            'filters',
        )
        extra_kwargs = {
            'url': {
                'lookup_field': 'uuid',
            },
            'documentatie_link': {
                'required': False,
                'validators': [URLValidator()],
            },
            'filters': {
                'required': False,
            }
        }


class FilterGroupSerializer(serializers.ModelSerializer):
    naam = serializers.CharField(source='kanaal.naam')
    filters = FiltersField(required=False)

    class Meta:
        model = FilterGroup
        fields = (
            'filters',
            'naam',
        )

        # delete unique validator for naam field - process it manually in AbonnementSerializer.create()
        extra_kwargs = {
            'naam': {
                'validators': [],
            }
        }


class AbonnementSerializer(serializers.HyperlinkedModelSerializer):
    kanalen = FilterGroupSerializer(source='filter_groups', many=True)

    class Meta:
        model = Abonnement
        fields = (
            'url',
            'callback_url',
            'auth',
            'kanalen',
        )
        extra_kwargs = {
            'url': {
                'lookup_field': 'uuid',
            },
            'callback_url': {
                'validators': [URLValidator()],
            },
            'auth': {
                'write_only': True,
            }
        }

    def validate(self, attrs):
        validated_attrs = super().validate(attrs)
        for group_data in validated_attrs.get('filter_groups', []):
            kanaal_data = group_data['kanaal']

            # check kanaal exists
            try:
                kanaal = Kanaal.objects.get(naam=kanaal_data['naam'])
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    {'naam': _('Kanaal met deze naam bestaat niet.')},
                    code='kanaal_naam')

            # check abonnement filters are consistent with kanaal filters
            abon_filter_names = [f.key for f in group_data['filters']]
            if not kanaal.match_filter_names(abon_filter_names):
                raise serializers.ValidationError(
                    {'filters': _("abonnement filters aren't consistent with kanaal filters")},
                    code='inconsistent-abonnement-filters')

        return validated_attrs

    def _create_kanalen_filters(self, abonnement, validated_data):
        for group_data in validated_data:
            kanaal_data = group_data.pop('kanaal')
            filters = group_data.pop('filters')

            kanaal = Kanaal.objects.get(naam=kanaal_data['naam'])
            filter_group = FilterGroup.objects.create(kanaal=kanaal, abonnement=abonnement)
            for filter in filters:
                filter.filter_group = filter_group
                filter.save()

    @transaction.atomic
    def create(self, validated_data):
        groups = validated_data.pop('filter_groups')
        abonnement = super().create(validated_data)
        self._create_kanalen_filters(abonnement, groups)
        return abonnement

    @transaction.atomic
    def update(self, instance, validated_data):
        groups = validated_data.pop('filter_groups', [])
        abonnement = super().update(instance, validated_data)

        # in case of update - delete all related kanalen and filters
        # and create them from request data
        abonnement.filter_groups.all().delete()

        self._create_kanalen_filters(abonnement, groups)
        return abonnement


class MessageSerializer(NotificatieSerializer):
    def validate(self, attrs):
        validated_attrs = super().validate(attrs)
        # check if exchange exists
        try:
            kanaal = Kanaal.objects.get(naam=validated_attrs['kanaal'])
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                {'kanaal': _('Kanaal met deze naam bestaat niet.')},
                code='message_kanaal')

        # check if msg kenmerken are consistent with kanaal filters
        kenmerken_names = list(validated_attrs['kenmerken'].keys())
        if not kanaal.match_filter_names(kenmerken_names):
            raise serializers.ValidationError(
                {'kenmerken': _("Kenmerken aren't consistent with kanaal filters")},
                code='kenmerken_inconsistent')

        # ensure we're still camelCasing
        return camelize(validated_attrs)

    def _send_to_subs(self, msg: dict):
        # define subs
        msg_filters = msg['kenmerken']
        subs = set()
        filter_groups = FilterGroup.objects.filter(kanaal__naam=msg['kanaal'])
        for group in filter_groups:
            if group.match_pattern(msg_filters):
                subs.add(group.abonnement)

        # creation of the notification
        kanaal = Kanaal.objects.get(naam=msg['kanaal'])
        notificatie = Notificatie.objects.create(forwarded_msg=msg, kanaal=kanaal)

        # send to subs
        for sub in list(subs):
            deliver_message.delay(sub.id, msg, notificatie.id)

    def _send_to_queue(self, msg):
        settings.CHANNEL.set_exchange(msg['kanaal'])
        topics = Kanaal.objects.get(naam=msg['kanaal']).filters
        settings.CHANNEL.set_routing_key_encoded(topics)
        settings.CHANNEL.send(json.dumps(msg, cls=DjangoJSONEncoder))

    def create(self, validated_data: dict) -> dict:
        # remove sending to queue because of connection issues
        # self._send_to_queue(validated_data)

        # send to subs
        self._send_to_subs(validated_data)
        return validated_data
