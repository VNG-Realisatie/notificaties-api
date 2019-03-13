import logging

from rest_framework import viewsets

from vng_api_common.permissions import ActionScopesRequired
from vng_api_common.viewsets import CheckQueryParamsMixin


from .scopes import (
    SCOPE_SUB_READ_ALL, SCOPE_SUB_CHANGE_ALL
)
from .serializers import AbonnementSerializer, KanaalSerializer
from notifications.datamodel.models import Abonnement, Kanaal

logger = logging.getLogger(__name__)


class AbonnementViewSet(CheckQueryParamsMixin,
                        viewsets.ModelViewSet):

    queryset = Abonnement.objects.all()
    serializer_class = AbonnementSerializer
    lookup_field = 'uuid'

    permission_classes = (ActionScopesRequired,)
    required_scopes = {
        'list': SCOPE_SUB_READ_ALL,
        'retrieve': SCOPE_SUB_READ_ALL,
        'create': SCOPE_SUB_CHANGE_ALL,
        'destroy': SCOPE_SUB_CHANGE_ALL,
        'update': SCOPE_SUB_CHANGE_ALL,
        'partial_update': SCOPE_SUB_CHANGE_ALL,
    }


class KanaalViewSet(CheckQueryParamsMixin,
                    viewsets.ModelViewSet):

    queryset = Kanaal.objects.all()
    serializer_class = KanaalSerializer
    lookup_field = 'uuid'
    permission_classes = (ActionScopesRequired,)
    required_scopes = {
        'list': SCOPE_SUB_READ_ALL,
        'retrieve': SCOPE_SUB_READ_ALL,
        'create': SCOPE_SUB_CHANGE_ALL,
        'destroy': SCOPE_SUB_CHANGE_ALL,
        'update': SCOPE_SUB_CHANGE_ALL,
        'partial_update': SCOPE_SUB_CHANGE_ALL,
    }
