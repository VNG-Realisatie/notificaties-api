import logging

from rest_framework import mixins, status, viewsets, views
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from vng_api_common.permissions import ActionScopesRequired
from vng_api_common.viewsets import CheckQueryParamsMixin
from drf_yasg.utils import swagger_auto_schema

from notifications.datamodel.models import Abonnement, Kanaal

from .scopes import SCOPE_NOTIF_CHANGE_ALL, SCOPE_NOTIF_READ_ALL
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
        'list': SCOPE_NOTIF_READ_ALL,
        'retrieve': SCOPE_NOTIF_READ_ALL,
        'create': SCOPE_NOTIF_CHANGE_ALL,
        'destroy': SCOPE_NOTIF_CHANGE_ALL,
        'update': SCOPE_NOTIF_CHANGE_ALL,
        'partial_update': SCOPE_NOTIF_CHANGE_ALL,
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
        'list': SCOPE_NOTIF_READ_ALL,
        'retrieve': SCOPE_NOTIF_READ_ALL,
        'create': SCOPE_NOTIF_CHANGE_ALL,
        'destroy': SCOPE_NOTIF_CHANGE_ALL,
        'update': SCOPE_NOTIF_CHANGE_ALL,
        'partial_update': SCOPE_NOTIF_CHANGE_ALL,
    }


class NotificatieAPIView(views.APIView):

    parser_classes = (JSONParser,)
    permission_classes = (ActionScopesRequired,)
    required_scopes = {
        'list': SCOPE_NOTIF_READ_ALL,
        'retrieve': SCOPE_NOTIF_READ_ALL,
        'create': SCOPE_NOTIF_CHANGE_ALL,
        'destroy': SCOPE_NOTIF_CHANGE_ALL,
        'update': SCOPE_NOTIF_CHANGE_ALL,
        'partial_update': SCOPE_NOTIF_CHANGE_ALL,
    }
    action = 'create'

    def create(self, request, *args, **kwargs):
        return self.post(self, request, *args, **kwargs)

    @swagger_auto_schema(request_body=MessageSerializer, responses={200: MessageSerializer})
    def post(self, request, *args, **kwargs):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            # post to message queue
            # send to abonnement
            serializer.save()

            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
