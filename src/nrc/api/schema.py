from django.conf import settings

__all__ = [
    "TITLE",
    "DESCRIPTION",
    "CONTACT",
    "LICENSE",
    "VERSION",
]
TITLE = f"{settings.PROJECT_NAME} API"
DESCRIPTION = f"""
The API consists of three parts:
    1. **Publishing events (resource Events)** <br> The events resource is based on the [GOV NL profile for CloudEvents](https://vng-realisatie.github.io/NL-GOV-profile-for-CloudEvents).
      This specification only contains brief descriptions of the attributes of the event. Please refer to the GOV NL profile for additional information.
    2. **Subscribing to receive events (resource Subscriptions)**<br>
    The subscription resource was derived from the [CloudEvents Subscription v1.0.0-wip](https://github.com/cloudevents/spec/tree/main/subscriptions).
    This specification only contains brief descriptions of the attributes of the subscription. Please refer to the draft CE Subscription Specification for additional information.
    3. **Basic information about domains (resource Domains)** <br>The scopes for autorisation are described [here](https://github.com/VNG-Realisatie/notificatieservices/blob/main/docs/api-specification/scopes.md).
    This specification is work in progress. It can be changed completely without notice.
"""

CONTACT = {
    "email": "standaarden.ondersteuning@vng.nl",
    "url": settings.DOCUMENTATION_URL,
}
LICENSE = {"name": "EUPL 1.2", "url": "https://opensource.org/licenses/EUPL-1.2"}
VERSION = settings.API_VERSION
