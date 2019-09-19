# Resources

Dit document beschrijft de (RGBZ-)objecttypen die als resources ontsloten
worden met de beschikbare attributen.


## FilterGroup

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_1.0/doc/objecttype/filtergroup)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| filters | Map van kenmerken (sleutel/waarde) waarop notificaties gefilterd worden. Alleen notificaties waarvan de kenmerken voldoen aan het filter worden doorgestuurd naar de afnemer van het ABONNEMENT. | object | nee | C​R​U​D |
| naam | De naam van het KANAAL (`KANAAL.naam`) waarop een abonnement is of wordt genomen. | string | ja | C​R​U​D |

## Abonnement

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_1.0/doc/objecttype/abonnement)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| url | URL-referentie naar dit object. Dit is de unieke identificatie en locatie van dit object. | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| callbackUrl | De URL waar notificaties naar toe gestuurd dienen te worden. Deze URL dient uit te komen bij een API die geschikt is om notificaties op te ontvangen. | string | ja | C​R​U​D |
| auth | Autorisatie header invulling voor het vesturen naar de &quot;Callback URL&quot;. Voorbeeld: Bearer a4daa31... | string | ja | C​R​U​D |
| kanalen | Een lijst van kanalen en filters waarop het ABONNEMENT wordt afgenomen. | array | ja | C​R​U​D |

## Kanaal

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_1.0/doc/objecttype/kanaal)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| url | URL-referentie naar dit object. Dit is de unieke identificatie en locatie van dit object. | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| naam | Naam van het KANAAL (ook wel &quot;Exchange&quot; genoemd) dat de bron vertegenwoordigd. | string | ja | C​R​U​D |
| documentatieLink | URL naar documentatie. | string | nee | C​R​U​D |
| filters | Lijst van mogelijke filter kenmerken van een KANAAL. Deze filter kenmerken kunnen worden gebruikt bij het aanmaken van een ABONNEMENT. | array | nee | C​R​U​D |


* Create, Read, Update, Delete
