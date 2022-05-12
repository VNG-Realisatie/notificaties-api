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
