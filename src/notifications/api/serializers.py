import logging
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from notifications.datamodel.models import Abonnement, Filter, Kanaal


logger = logging.getLogger(__name__)


class FilterSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {data['key']: data['value']}

    def to_internal_value(self, data):
        if len(data) > 1:
            raise serializers.ValidationError(
                {'filter': "'filter dict must have only one element')"},
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
        )
        extra_kwargs = {
            'url': {
                'lookup_field': 'uuid',
            },
            'documentatie_link': {
                'required': False,
            }
        }


class AbonnementKanaalSerializer(KanaalSerializer):
    filters = FilterSerializer(many=True, required=False)

    class Meta(KanaalSerializer.Meta):
        fields = KanaalSerializer.Meta.fields + ('filters',)

        # delete unique validator for naam field - process it manually in AbonnementSerializer.create()
        extra_kwargs = {
            **KanaalSerializer.Meta.extra_kwargs,
            **{
                'naam': {
                    'validators': [],
                }
            }
        }


class AbonnementSerializer(serializers.HyperlinkedModelSerializer):
    kanalen = AbonnementKanaalSerializer(many=True)

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

    def _create_kanalen_filters(self, abonnement, validated_data):
        for kanaal_data in validated_data:
            try:
                kanaal = Kanaal.objects.get(naam=kanaal_data['naam'])
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    {'naam': "Kannal with this name dosn't exist"},
                    code='kanaal_naam')
            filters = kanaal_data.pop('filters')
            abonnement.kanalen.add(kanaal)
            for filter in filters:
                filter.kanaal = kanaal
                filter.abonnement = abonnement
                filter.save()

    def create(self, validated_data):
        kanalen = validated_data.pop('kanalen')
        abonnement = super().create(validated_data)
        self._create_kanalen_filters(abonnement, kanalen)
        return abonnement

    def update(self, instance, validated_data):
        kanalen = validated_data.pop('kanalen')
        abonnement = super().update(instance, validated_data)

        # in case of update - delete all related kanalen and filters
        # and create them from request data
        abonnement.kanalen.all().delete()
        Filter.objects.filter(abonnement=abonnement).delete()

        self._create_kanalen_filters(abonnement, kanalen)
        return abonnement
