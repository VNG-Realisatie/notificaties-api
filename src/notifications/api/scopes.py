"""
Defines the scopes used in the ZRC component.

The Exxellence authorisation model is taken into consideration as well, see
https://wiki.exxellence.nl/display/KPORT/2.+Zaaktype+autorisaties
"""

from vng_api_common.scopes import Scope

SCOPE_SUB_READ_ALL = Scope(
    'zds.scopes.sub.read',
    description="""
**Allows**:

* list subscribers
* request subscriber details
"""
)

SCOPE_SUB_CHANGE_ALL = Scope(
    'zds.scopes.sub.change',
    description="""
**Allows**:

* create subscriber
* change attributes of subscriber
* delete subscriber
"""
)
