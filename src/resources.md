# Resources

Dit document beschrijft de (RGBZ-)objecttypen die als resources ontsloten
worden met de beschikbare attributen.


## FilterGroup

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_1.0/doc/objecttype/filtergroup)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| filters |  | object | nee | C​R​U​D |
| naam |  | string | ja | C​R​U​D |

## Abonnement

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_1.0/doc/objecttype/abonnement)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| url |  | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| callbackUrl | De URL waar notificaties naar toe gestuurd dienen te worden. Deze URL dient uit te komen bij een API die geschikt is om notificaties op te ontvangen. | string | ja | C​R​U​D |
| auth | Autorisatie header invulling voor het vesturen naar de &quot;Callback URL&quot;. Voorbeeld: Bearer a4daa31... | string | ja | C​R​U​D |
| kanalen |  | array | ja | C​R​U​D |

## Kanaal

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_1.0/doc/objecttype/kanaal)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| url |  | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| naam | Naam van het kanaal (ook wel &quot;Exchange&quot; genoemd) dat de bron vertegenwoordigd. | string | ja | C​R​U​D |
| documentatieLink | URL naar documentatie. | string | nee | C​R​U​D |
| filters | Comma-separated list of filters of the kanaal | array | nee | C​R​U​D |


* Create, Read, Update, Delete
