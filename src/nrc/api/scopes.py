"""
Defines the scopes used in the NC component.
"""

from vng_api_common.scopes import Scope

SCOPE_SUBSCRIPTIONS_READ = Scope(
    "subscriptions.read",
    description="""
**Laat toe om**:

* subscription te lezen
* subscriptions te lezen
""",
)

SCOPE_SUBSCRIPTIONS_CREATE = Scope(
    "subscriptions.create",
    description="""
**Laat toe om**:

* subscription aan te maken
""",
)

SCOPE_SUBSCRIPTIONS_UPDATE = Scope(
    "subscriptions.update",
    description="""
**Laat toe om**:

* subscription te wijzigen
* subscription gedeeltelijk te wijzigen
""",
)


SCOPE_SUBSCRIPTIONS_DELETE = Scope(
    "subscriptions.delete",
    description="""
**Laat toe om**:

* subscription te lezen
* subscriptions te lezen
""",
)

SCOPE_DOMAINS_READ = Scope(
    "domains.read",
    description="""
**Laat toe om**:

* domain te lezen
* domains te lezen
""",
)


SCOPE_DOMAINS_CREATE = Scope(
    "domains.create",
    description="""
**Laat toe om**:

* domain aan te maken
""",
)

SCOPE_DOMAINS_UPDATE = Scope(
    "domains.update",
    description="""
**Laat toe om**:

* domains te wijzigen
* domains gedeeltelijk te wijzigen
""",
)


SCOPE_DOMAINS_DELETE = Scope(
    "domains.delete",
    description="""
**Laat toe om**:

* subscription te lezen
* subscriptions te lezen
""",
)

SCOPE_EVENTS_PUBLISH = Scope(
    "events.publish",
    description="""
**Laat toe om**:

* event te versturen aan dit component
* event te versturen aan abonnees
""",
)
