from django.conf import settings

from drf_yasg import openapi

description = """Een API om een notificaties te routeren.

Deze API voorziet in drie functionaliteiten voor notificaties:

* registreren van kanalen (=exchanges)
* abonneren van consumers op kanalen
* ontvangen en routeren van berichten

**Registreren van kanalen**

Een component dekt een bepaald domein af, en heeft het recht om hiervoor een
kanaal te registeren waarop eigen notificaties verstuurd worden. Een kanaal
is uniek in naam. Een component dient dus te controleren of een kanaal al
bestaat voor het registreren. Bij het registeren van kanalen wordt een
documentatielink verwacht die beschrijft welke events en kenmerken van
toepassing zijn op het kanaal.

**Abonneren**

Consumers kunnen een abonnement aanmaken voor een of meerdere kanalen. Per
kanaal kan op de kenmerken van het kanaal gefilterd worden. Consumers dienen
zelf een endpoint te bouwen waarop berichten afgeleverd (kunnen) worden.

**Routeren van berichten**

Bronnen sturen berichten naar deze API, die vervolgens de berichten onveranderd
routeert naar alle abonnees.

**Autorisatie**

Deze API vereist autorisatie. Je kan de
[token-tool](https://ref.tst.vng.cloud/tokens/) gebruiken om JWT-tokens te
genereren.

**Handige links**

* [Aan de slag](https://ref.tst.vng.cloud/ontwikkelaars/)
* [Aan de slag met notificeren](https://ref.tst.vng.cloud/ontwikkelaars/notificeren)
* ["Papieren" standaard](https://ref.tst.vng.cloud/standaard/)
"""

info = openapi.Info(
    title="Notificaties (NC) API",
    default_version=settings.API_VERSION,
    description=description,
    contact=openapi.Contact(
        email="support@maykinmedia.nl",
        url="https://github.com/VNG-Realisatie/gemma-zaken"
    ),
    license=openapi.License(
        name="EUPL 1.2",
        url='https://opensource.org/licenses/EUPL-1.2'
    ),
)
