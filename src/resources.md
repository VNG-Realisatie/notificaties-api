# Resources

Dit document beschrijft de (RGBZ-)objecttypen die als resources ontsloten
worden met de beschikbare attributen.


## Filter

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_1.0/doc/objecttype/filter)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| key |  | string | ja | C​R​U​D |
| value |  | string | ja | C​R​U​D |

## Kanaal

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_1.0/doc/objecttype/kanaal)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| url |  | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| naam | name of the channel/exchange | string | ja | C​R​U​D |
| filters |  | array | ja | C​R​U​D |

## Abonnement

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_1.0/doc/objecttype/abonnement)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| url |  | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| callbackUrl | Url of subscriber API to which NC will post messages | string | ja | C​R​U​D |
| auth | Authentication method to subscriber | string | nee | C​R​U​D |
| kanalen |  | array | ja | C​R​U​D |


* Create, Read, Update, Delete
