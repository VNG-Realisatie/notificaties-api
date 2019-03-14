"""
Defines the scopes used in the ZRC component.

The Exxellence authorisation model is taken into consideration as well, see
https://wiki.exxellence.nl/display/KPORT/2.+Zaaktype+autorisaties
"""

from vng_api_common.scopes import Scope

SCOPE_NOTIF_READ_ALL = Scope(
    'zds.scopes.notif.read',
    description="""
**Allows**:

* list subscribers
* request subscriber details
* list exchanges
* request exchange details
"""
)

SCOPE_NOTIF_CHANGE_ALL = Scope(
    'zds.scopes.notif.change',
    description="""
**Allows**:

* create subscriber
* change attributes of subscriber
* delete subscriber
* create exchanges
* change attributes of exchange
* delete exchanges
"""
)
