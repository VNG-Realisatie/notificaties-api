"""
Defines the scopes used in the NC component.
"""

from vng_api_common.scopes import Scope

SCOPE_EVENTS_CONSUMEREN = Scope(
    "events.consume",
    description="""
**Laat toe om**:

* domain aan te maken
* domain te wijzigen
* domain te verwijderen
* domain te lezen
* domainen te lezen
""",
)

SCOPE_EVENTS_PUBLICEREN = Scope(
    "events.publish",
    description="""
**Laat toe om**:

* domain te lezen
* domain aan te maken
* domain te wijzigen
* domain te verwijderen
* subscription te lezen
* event te versturen aan dit component
* event te versturen aan abonnees
""",
)
