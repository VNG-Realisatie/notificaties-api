import json
import logging

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import ugettext_lazy as _

import requests
from requests.exceptions import RequestException
from rest_framework import serializers

from notifications.datamodel.models import (
    Abonnement, Filter, FilterGroup, Kanaal, Notificatie, NotificatieResponse
)

logger = logging.getLogger(__name__)


class FilterSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {data['key']: data['value']}

    def to_internal_value(self, data):
        if len(data) > 1:
            raise serializers.ValidationError(
                {'filter': "filter dict must have only one element"},
                code='filter_many'
            )
        key = list(data)[0]
        value = data[key]
        return Filter(key=key, value=value)

    class Meta:
        model = Filter
        fields = (
            'key',
            'value',
        )


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
            },
            'filters': {
                'required': False,
            }
        }


class FilterGroupSerializer(serializers.ModelSerializer):
    filters = FilterSerializer(many=True, required=False)
    naam = serializers.CharField(source='kanaal.naam')

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
            'auth': {
                'write_only': True,
            }
        }

    def validate(self, attrs):
        validated_attrs = super().validate(attrs)
        for group_data in validated_attrs['filter_groups']:
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

    def create(self, validated_data):
        groups = validated_data.pop('filter_groups')
        abonnement = super().create(validated_data)
        self._create_kanalen_filters(abonnement, groups)
        return abonnement

    def update(self, instance, validated_data):
        groups = validated_data.pop('filter_groups')
        abonnement = super().update(instance, validated_data)

        # in case of update - delete all related kanalen and filters
        # and create them from request data
        abonnement.filter_groups.all().delete()

        self._create_kanalen_filters(abonnement, groups)
        return abonnement


class MessageSerializer(serializers.Serializer):
    kanaal = serializers.CharField(max_length=50)
    hoofdObject = serializers.URLField()
    resource = serializers.CharField(max_length=100)
    resourceUrl = serializers.URLField()
    actie = serializers.CharField(max_length=100)
    aanmaakdatum = serializers.DateTimeField()
    kenmerken = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(max_length=1000)
        )
    )

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
        kenmerken_names = [list(k)[0] for k in validated_attrs['kenmerken']]
        if not kanaal.match_filter_names(kenmerken_names):
            raise serializers.ValidationError(
                {'kenmerken': _("Kenmerken aren't consistent with kanaal filters")},
                code='kenmerken_inconsistent')

        return validated_attrs

    def _send_to_subs(self, msg):
        # define subs
        msg_filters = msg['kenmerken']
        subs = set()
        filter_groups = FilterGroup.objects.filter(kanaal__naam=msg['kanaal'])
        for group in filter_groups:
            if group.match_pattern(msg_filters):
                subs.add(group.abonnement)

        forwarded_msg = json.dumps(msg, cls=DjangoJSONEncoder)

        # creation of the notification
        kanaal = Kanaal.objects.get(naam=msg['kanaal'])
        notificatie = Notificatie.objects.create(forwarded_msg=forwarded_msg, kanaal=kanaal)

        # send to subs
        responses = []
        for sub in list(subs):
            try:
                response = requests.post(
                    sub.callback_url,
                    data=forwarded_msg,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': sub.auth
                    },
                )
                # log of the response of the call
                NotificatieResponse.objects.create(
                    notificatie=notificatie, abonnement=sub,
                    response_status=response.status_code
                )
            except RequestException as e:
                # log of the response of the call
                response = None
                NotificatieResponse.objects.create(
                    notificatie=notificatie, abonnement=sub,
                    exception=str(e)
                )

            responses.append(response)
        return responses

    def _send_to_queue(self, msg):
        settings.CHANNEL.set_exchange(msg['kanaal'])
        settings.CHANNEL.set_routing_key_encoded(msg['kenmerken'])
        settings.CHANNEL.send(json.dumps(msg, cls=DjangoJSONEncoder))

    def create(self, validated_data):
        # remove sending to queue because of connection issues
        # self._send_to_queue(validated_data)

        # send to subs
        responses = self._send_to_subs(validated_data)

        return responses
