from datetime import datetime

import dateutil.parser

default_app_config = 'notifications.utils.apps.UtilsConfig'


def parse_isodatetime(val) -> datetime:
    return dateutil.parser.parse(val)
