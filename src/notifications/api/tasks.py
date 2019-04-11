import json
import logging

from django.core.serializers.json import DjangoJSONEncoder

import requests

from notifications.celery import app
from notifications.datamodel.models import Abonnement, NotificatieResponse

logger = logging.getLogger(__name__)


@app.task
def deliver_message(sub_id: int, msg: dict, notificatie_id: int) -> None:
    """
    send msg to subscriber

    The delivery-result is logged in "NotificatieResponse"
    """
    try:
        sub = Abonnement.objects.get(pk=sub_id)
    except Abonnement.DoesNotExist:
        logger.warning("Could not retrieve abonnement %d, not delivering message", sub_id)
        return

    try:
        response = requests.post(
            sub.callback_url,
            data=json.dumps(msg, cls=DjangoJSONEncoder),
            headers={
                'Content-Type': 'application/json',
                'Authorization': sub.auth
            },
        )
        # log of the response of the call
        NotificatieResponse.objects.create(
            notificatie_id=notificatie_id,
            abonnement=sub,
            response_status=response.status_code
        )
    except requests.exceptions.RequestException as e:
        # log of the response of the call
        NotificatieResponse.objects.create(
            notificatie_id=notificatie_id,
            abonnement=sub,
            exception=str(e)
        )
