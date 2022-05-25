import json
import logging

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q

import requests

from nrc.celery import app
from nrc.datamodel.models import Event, EventResponse, Subscription

logger = logging.getLogger(__name__)


@app.task
def deliver_message(event_id: int) -> None:
    """
    send event to subscribers

    The delivery-result is logged in "EventResponse"
    """
    event = Event.objects.get(pk=event_id)

    source_filter = Q(source=event.forwarded_msg["source"])
    domain_filter = Q(domain=None) | Q(domain=event.domain)
    type_filter = (
        Q(
            types__contains=[event.forwarded_msg["type"]],
        )
        | Q(types=[])
        | Q(types=None)
    )

    subscriptions = Subscription.objects.filter(
        source_filter, type_filter, domain_filter
    )

    for subscription in subscriptions:
        extra_headers = {}

        if subscription.protocol_settings:
            extra_headers = subscription.protocol_settings.get("headers", {})

        if subscription.sink_credential and subscription.sink_credential.get(
            "access_token"
        ):
            access_token = subscription.sink_credential["access_token"]
            extra_headers.update({"Authorization": f"bearer {access_token}"})

        logger.debug(f"Sending event {event_id} to subscription {subscription.uuid}")

        try:
            response = requests.post(
                subscription.sink,
                data=json.dumps(event.forwarded_msg, cls=DjangoJSONEncoder),
                headers={
                    **extra_headers,
                    "Content-Type": "application/json",
                },
            )
            # log of the response of the call
            EventResponse.objects.create(
                event=event,
                subscription=subscription,
                response_status=response.status_code,
            )
        except requests.exceptions.RequestException as e:
            # log of the response of the call
            EventResponse.objects.create(
                event=event, subscription=subscription, exception=str(e)
            )
