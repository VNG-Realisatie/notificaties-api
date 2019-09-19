"""
Defines the scopes used in the NC component.
"""

from vng_api_common.scopes import Scope

SCOPE_NOTIFICATIES_CONSUMEREN = Scope(
    "notificaties.consumeren",
    description="""
**Laat toe om**:

* abonnementen aan te maken
* abonnementen te wijzigen
* abonnementen te verwijderen
* abonnementen te lezen
* kanalen te lezen
""",
)

SCOPE_NOTIFICATIES_PUBLICEREN = Scope(
    "notificaties.publiceren",
    description="""
**Laat toe om**:

* kanalen te lezen
* kanalen aan te maken
* kanalen te wijzigen
* kanalen te verwijderen
* abonnementen te lezen
* notificaties te versturen aan dit component
* notificaties te versturen aan abonnees
""",
)
