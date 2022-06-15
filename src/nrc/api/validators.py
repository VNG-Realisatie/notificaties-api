import binascii
from base64 import b64decode
from urllib.parse import urlparse
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

import requests
from rest_framework import serializers

from nrc.api.choices import SequencetypeChoices
from nrc.api.filters import AllFilterNode


class CallbackURLValidator:
    code = "invalid-callback-url"
    message = _("De opgegeven callback URL kan geen notificaties ontvangen.")

    def __init__(self, url_field: str):
        self.url_field = url_field

    def set_context(self, serializer):
        if serializer.partial:
            self.url_from_instance = serializer.instance.sink

    def __call__(self, attrs):
        url = attrs.get(self.url_field)
        if not url and hasattr(self, "url_from_instance"):
            url = self.url_from_instance

        protocol_settings = attrs.get("protocol_settings", {}) or {}
        headers = protocol_settings.get("headers", {}) or {}

        if "sink_credential" in attrs and attrs["sink_credential"]:
            access_token = attrs["sink_credential"]["access_token"]

            headers.update({"Authorization": f"bearer {access_token}"})

        try:
            response = requests.post(
                url,
                json={
                    "id": str(uuid4()),
                    "specversion": "1.0",
                    "source": "urn:nld:oin:00000001234567890000:systeem:Zaaksysteem",
                    "domain": "nl.vng.test",
                    "type": "nl.vng.test.status_gewijzigd",
                    "time": "2022-03-16T15:29:30.833664Z",
                    "subscription": str(uuid4()),
                    "datacontenttype": "application/json",
                    "dataschema": "https://vng.nl/zgw/zaken/status_gewijzigd_schema.json",
                    "sequence": "1",
                    "sequencetype": SequencetypeChoices.integer,
                    "data": {"foo": "bar", "bar": "foo"},
                },
                headers=headers,
                verify=False,
            )
        except requests.RequestException:
            raise serializers.ValidationError(self.message, code=self.code)

        if response.status_code != 204:
            raise serializers.ValidationError(self.message, code=self.code)


class CallbackURLAuthValidator:
    code = "no-auth-on-callback-url"
    message = _("De opgegeven callback URL is niet beveiligd met autorisatie.")
    default_whitelist = ["webhook.site"]

    def __init__(self, whitelist=None):
        self.whitelist = whitelist or self.default_whitelist

    def __call__(self, url):
        if not settings.TEST_CALLBACK_AUTH:
            return

        parsed = urlparse(url)
        if parsed.netloc in self.whitelist:
            return

        response = requests.post(
            url,
            json={
                "kanaal": "test",
                "hoofdObject": "http://some.hoofdobject.nl/",
                "resource": "some_resource",
                "resourceUrl": "http://some.resource.nl/",
                "actie": "create",
                "aanmaakdatum": "2019-01-01T12:00:00Z",
                "kenmerken": {},
            },
        )

        if response.status_code != 403:
            raise serializers.ValidationError(self.message, code=self.code)


class Base64Validator:
    code = "invalid-value"
    message = _("De opgegeven waarde is geen valide base64.")

    def __call__(self, value):
        try:
            b64decode(value)
        except (binascii.Error, TypeError):
            raise serializers.ValidationError(self.message, code=self.code)


class FilterValidator:
    code = "invalid-value"
    message = _("De opgegeven filter is niet valide.")

    def __call__(self, value):
        filter = AllFilterNode(value)

        try:
            return filter.cast()
        except ValueError as e:
            raise ValidationError(self.message, code=self.code) from e
