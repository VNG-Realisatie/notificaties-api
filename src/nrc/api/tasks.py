import json
import logging

from django.core.serializers.json import DjangoJSONEncoder

import requests

from nrc.celery import app
from nrc.datamodel.models import EventResponse, Subscription

logger = logging.getLogger(__name__)


@app.task
def deliver_message(sub_id: int, msg: dict, event_id: int) -> None:
    """
    send msg to subscriber

    The delivery-result is logged in "EventResponse"
    """
    try:
        subscription = Subscription.objects.get(pk=sub_id)
    except Subscription.DoesNotExist:
        logger.warning(
            "Could not retrieve subscription %d, not delivering message", sub_id
        )
        return

    extra_headers = {}
    if subscription.protocol_settings:
        extra_headers = subscription.protocol_settings.get("headers", {})

    try:
        response = requests.post(
            subscription.sink,
            data=json.dumps(msg, cls=DjangoJSONEncoder),
            headers={
                **extra_headers,
                "Content-Type": "application/json",
            },
        )
        # log of the response of the call
        EventResponse.objects.create(
            event_id=event_id,
            subscription=subscription,
            response_status=response.status_code,
        )
    except requests.exceptions.RequestException as e:
        # log of the response of the call
        EventResponse.objects.create(
            event_id=event_id, subscription=subscription, exception=str(e)
        )
