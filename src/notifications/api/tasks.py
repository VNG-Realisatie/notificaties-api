from notifications.celery import app
import requests
from notifications.datamodel.models import NotificatieResponse, Abonnement


@app.task
def send_msg_to_sub_task(sub_id, msg, notificatie_id):
    """
    send task to subscriber
    Write results to NotificatieResponse
    """
    sub = Abonnement.objects.get(id=sub_id)
    try:
        response = requests.post(
            sub.callback_url,
            data=msg,
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
