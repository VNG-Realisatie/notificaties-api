from django.conf import settings

from drf_yasg import openapi

description = """Een API om een notificatierouteringscomponent te benaderen.

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

**Afhankelijkheden**

Deze API is afhankelijk van:

* Autorisaties API

### Autorisatie

Deze API vereist autorisatie.

_Zelf een token genereren_

De tokens die gebruikt worden voor autorisatie zijn 
[jwt.io][JWT's] (JSON web token). In de API calls moeten deze gebruikt worden in de 
`Authorization` header:

```
Authorization: Bearer <token>
```

Om een JWT te genereren heb je een `client ID` en een `secret` nodig. Het JWT moet 
gebouwd worden volgens het `HS256` algoritme. De vereiste payload is: 

```json
{
    "iss": "<client ID>", 
    "iat": 1572863906, 
    "client_id": "<client ID>", 
    "user_id": "<user identifier>", 
    "user_representation": "<user representation>" 
}
```

Als `issuer` gebruik je dus je eigen client ID. De `iat` timestamp is een 
UNIX-timestamp die aangeeft op welk moment het token gegenereerd is. 

**Handige links**

* [Documentatie](https://zaakgerichtwerken.vng.cloud/standaard)
* [Zaakgericht werken](https://zaakgerichtwerken.vng.cloud)
"""

info = openapi.Info(
    title=f"{settings.PROJECT_NAME} API",
    default_version=settings.API_VERSION,
    description=description,
    contact=openapi.Contact(
        email=settings.OPENNOTIFICATIES_API_CONTACT_EMAIL,
        url=settings.OPENNOTIFICATIES_API_CONTACT_URL,
    ),
    license=openapi.License(
        name="EUPL 1.2", url="https://opensource.org/licenses/EUPL-1.2"
    ),
)
