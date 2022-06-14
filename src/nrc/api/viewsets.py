import logging

from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status, views, viewsets
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from vng_api_common.viewsets import CheckQueryParamsMixin

from nrc.api.parsers import SubscriptionParser
from nrc.api.serializers import (
    DomainSerializer,
    EventSerializer,
    SubscriptionSerializer,
)
from nrc.datamodel.models import Domain, Subscription

from .filters import DomainFilter
from .scopes import SCOPE_EVENTS_CONSUMEREN, SCOPE_EVENTS_PUBLICEREN

logger = logging.getLogger(__name__)


class SubscriptionViewSet(
    CheckQueryParamsMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    list:
    Returns a list with information about all subscriptions.

    create:
    Subscribe to receive events.

    retrieve:
    Returns information about the specified subscription.

    update:
    Update the specified subscription by replacing all properties.

    destroy:
    Delete the specified subscription.
    """

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    lookup_field = "uuid"
    required_scopes = {
        "list": SCOPE_EVENTS_CONSUMEREN | SCOPE_EVENTS_PUBLICEREN,
        "retrieve": SCOPE_EVENTS_CONSUMEREN | SCOPE_EVENTS_PUBLICEREN,
        "create": SCOPE_EVENTS_CONSUMEREN,
        "destroy": SCOPE_EVENTS_CONSUMEREN,
        "update": SCOPE_EVENTS_CONSUMEREN,
    }

    parser_classes = (SubscriptionParser,)


class DomainViewSet(
    CheckQueryParamsMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    list:
    Returns a list with information about all domains.

    create:
    Defines a new domain with its basis properties and filter attributes.

    retrieve:
    Returns information about the specified domain.
    """

    queryset = Domain.objects.all()
    serializer_class = DomainSerializer
    filterset_class = DomainFilter
    lookup_field = "uuid"
    required_scopes = {
        "list": SCOPE_EVENTS_PUBLICEREN | SCOPE_EVENTS_CONSUMEREN,
        "retrieve": SCOPE_EVENTS_PUBLICEREN | SCOPE_EVENTS_CONSUMEREN,
        "create": SCOPE_EVENTS_PUBLICEREN,
    }


class EventAPIView(views.APIView):
    """
    Publish an event.

    The component will distribute the event to the subscribers when the criteria
    of a subscription are met.
    """

    required_scopes = {"create": SCOPE_EVENTS_PUBLICEREN}
    # Exposed action of the view used by the vng_api_common
    action = "create"

    parser_classes = (JSONParser,)
    renderer_classes = (JSONRenderer,)

    @swagger_auto_schema(request_body=EventSerializer, responses={200: EventSerializer})
    def create(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = EventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # post to message queue
        # send to abonnement
        serializer.save()

        return Response(data, status=status.HTTP_200_OK)
