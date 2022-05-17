from djangorestframework_camel_case.parser import CamelCaseJSONParser


class SubscriptionParser(CamelCaseJSONParser):
    """
    Ignores certain fields as they are often user defined.
    """

    json_underscoreize = {
        "ignore_fields": {
            "protocol_settings": {"headers": 1},
            "config": 1,
        },
    }


class EventParser(CamelCaseJSONParser):
    """
    Ignore fields based on the (in draft) Cloud Events spec
    """

    json_underscoreize = {
        "no_underscore_before_number": True,
        "ignore_fields": ("data_base64",),
    }
