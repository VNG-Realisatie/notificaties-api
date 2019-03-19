import logging

from rest_framework import mixins, status, viewsets
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from vng_api_common.permissions import ActionScopesRequired
from vng_api_common.viewsets import CheckQueryParamsMixin

from notifications.datamodel.models import Abonnement, Kanaal

from .scopes import SCOPE_NOTIFICATIES_CONSUMEREN, SCOPE_NOTIFICATIES_PUBLICEREN
from .serializers import (
    AbonnementSerializer, KanaalSerializer, MessageSerializer
)

logger = logging.getLogger(__name__)


class AbonnementViewSet(CheckQueryParamsMixin,
                        viewsets.ModelViewSet):

    queryset = Abonnement.objects.all()
    serializer_class = AbonnementSerializer
    lookup_field = 'uuid'
    permission_classes = (ActionScopesRequired,)
    required_scopes = {
        'list': SCOPE_NOTIFICATIES_CONSUMEREN | SCOPE_NOTIFICATIES_PUBLICEREN,
        'retrieve': SCOPE_NOTIFICATIES_CONSUMEREN | SCOPE_NOTIFICATIES_PUBLICEREN,
        'create': SCOPE_NOTIFICATIES_CONSUMEREN,
        'destroy': SCOPE_NOTIFICATIES_CONSUMEREN,
        'update': SCOPE_NOTIFICATIES_CONSUMEREN,
        'partial_update': SCOPE_NOTIFICATIES_CONSUMEREN,
    }


class KanaalViewSet(CheckQueryParamsMixin,
                    mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):

    queryset = Kanaal.objects.all()
    serializer_class = KanaalSerializer
    lookup_field = 'uuid'
    permission_classes = (ActionScopesRequired,)
    required_scopes = {
        'list': SCOPE_NOTIFICATIES_PUBLICEREN | SCOPE_NOTIFICATIES_CONSUMEREN,
        'retrieve': SCOPE_NOTIFICATIES_PUBLICEREN | SCOPE_NOTIFICATIES_CONSUMEREN,
        'create': SCOPE_NOTIFICATIES_PUBLICEREN,
        'destroy': SCOPE_NOTIFICATIES_PUBLICEREN,
        'update': SCOPE_NOTIFICATIES_PUBLICEREN,
        'partial_update': SCOPE_NOTIFICATIES_PUBLICEREN,
    }


class NotificatieViewSet(viewsets.ViewSet):
    # FIXME: The schema needs to work but requires a queryset for drf...
    swagger_schema = None

    serializer_class = MessageSerializer
    parser_classes = (JSONParser,)
    permission_classes = (ActionScopesRequired,)
    required_scopes = {
        'list': SCOPE_NOTIFICATIES_PUBLICEREN,
        'retrieve': SCOPE_NOTIFICATIES_PUBLICEREN,
        'create': SCOPE_NOTIFICATIES_PUBLICEREN,
        'destroy': SCOPE_NOTIFICATIES_PUBLICEREN,
        'update': SCOPE_NOTIFICATIES_PUBLICEREN,
        'partial_update': SCOPE_NOTIFICATIES_PUBLICEREN,
    }

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            # post to message queue
            # send to abonnement
            serializer.save()

            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
