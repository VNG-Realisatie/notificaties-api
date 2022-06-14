from django.conf import settings

from drf_yasg import openapi

description = f"""
The API consists of three parts:
    1. **Publishing events (resource Events)** <br> The events resource is based on the [GOV NL profile for CloudEvents](https://vng-realisatie.github.io/NL-GOV-profile-for-CloudEvents).
      This specification only contains brief descriptions of the attributes of the event. Please refer to the GOV NL profile for additional information.
    2. **Subscribing to receive events (resource Subscriptions)**<br>
    The subscription resource was derived from the [CloudEvents Subscription v1.0.0-wip](https://github.com/cloudevents/spec/tree/main/subscriptions).
    This specification only contains brief descriptions of the attributes of the subscription. Please refer to the draft CE Subscription Specification for additional information.
    3. **Basic information about domains (resource Domains)** <br>The scopes for autorisation are described [here](https://github.com/VNG-Realisatie/notificatieservices/blob/main/docs/api-specification/scopes.md).
    This specification is work in progress. It can be changed completely without notice.
"""

info = openapi.Info(
    title=f"{settings.PROJECT_NAME} API",
    default_version=settings.API_VERSION,
    description=description,
    license=openapi.License(
        name="EUPL 1.2", url="https://opensource.org/licenses/EUPL-1.2"
    ),
)
