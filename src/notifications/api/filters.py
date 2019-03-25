from vng_api_common.filtersets import FilterSet

from notifications.datamodel.models import Kanaal


class KanaalFilter(FilterSet):
    class Meta:
        model = Kanaal
        fields = (
            'naam',
        )
