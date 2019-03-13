import logging

from rest_framework import serializers

from notifications.datamodel.models import Abonnement, Kanaal, Filter


logger = logging.getLogger(__name__)


class FilterSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {data['key']: data['value']}

    def to_internal_value(self, data):
        if len(data) > 1:
            raise serializers.ValidationError('filter dict must have only one element')
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
    filters = FilterSerializer(many=True)

    class Meta:
        model = Kanaal
        fields = (
            'url',
            'naam',
            'filters',
        )
        extra_kwargs = {
            'url': {
                'lookup_field': 'uuid',
            }
        }

    def create(self, validated_data):
        filters = validated_data.pop('filters')
        kanaal = super().create(validated_data)
        for filter in filters:
            filter.kanaal = kanaal
            filter.save()
        return kanaal


class AbonnementSerializer(serializers.HyperlinkedModelSerializer):
    kanalen = KanaalSerializer(many=True)

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
            },
        }

    def create(self, validated_data):
        kanaal_serializer = self.fields['kanalen']
        kanalen = validated_data.pop('kanalen')
        abonnement = super().create(validated_data)
        for kanaal_data in kanalen:
            kanaal_data['abonnement'] = abonnement
            kanaal_serializer.create([kanaal_data])
        return abonnement

    def update(self, instance, validated_data):
        kanaal_serializer = self.fields['kanalen']
        kanalen = validated_data.pop('kanalen')
        abonnement = super().update(instance, validated_data)

        # in case of update - delete all related kanalen and create them from request data
        Kanaal.objects.filter(abonnement=abonnement).delete()
        for kanaal_data in kanalen:
            kanaal_data['abonnement'] = abonnement
            kanaal_serializer.create([kanaal_data])
        return abonnement
