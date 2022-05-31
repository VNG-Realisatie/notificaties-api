# Resources

Dit document beschrijft de (RGBZ-)objecttypen die als resources ontsloten
worden met de beschikbare attributen.


## Domain

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_1.0/doc/objecttype/domain)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| name | Naam van het DOMAIN dat de bron vertegenwoordigd. | string | ja | C​R​U​D |
| documentationLink | URL naar documentatie. | string | nee | C​R​U​D |
| filterAttributes | Filtering op EVENTs op basis van opgegeven attributen | array | nee | C​R​U​D |

## Event

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_1.0/doc/objecttype/event)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| id | ID van het EVENT. | string | ja | C​R​U​D |
| specversion | De versie van de CloudEvents specificatie welke het EVENT gebruikt. | string | ja | C​R​U​D |
| source | Identificeert de context waarin een EVENT heeft plaatsgevonden. | string | ja | C​R​U​D |
| domain | Naam van het DOMAIN waartoe het EVENT behoort. | string | ja | C​R​U​D |
| type | Beschrijft het type EVENT afkomstig van het specifieke DOMAIN. | string | ja | C​R​U​D |
| time | Tijdstempel van wanneer het EVENT heeft plaatgevonden. | string | nee | C​R​U​D |
| subscription | De gebeurtenis is naar de API gepost omdat aan de filtercriteria van deze SUBSCRIPTION is voldaan. De uuid verwijst naar een SUBSCRIPTION op de bron die deze EVENT heeft gepubliceerd. Het moet worden doorgegeven wanneer dit EVENT wordt afgeleverd bij SUBSCRIPTIONs. Wanneer een EVENT wordt gedistribueerd naar een SUBSCRIPTION, moet dit kenmerk worden overschreven (of ingevuld) met de SUBSCRIPTION&#x27;s uuid van de abonnee die de levering heeft geactiveerd. | string | nee | C​R​U​D |
| datacontenttype | Content-type van de meegegeven data. | string | nee | C​R​U​D |
| dataschema | Identificeert het schema waarmee de data gevalideerd kan worden. | string | nee | C​R​U​D |
| sequence | Volgorde van het EVENT. Dit maakt het mogelijk meerdere opeenvolgende EVENTs te versturen. | string | nee | C​R​U​D |
| sequencetype | Specificeert het type van de opgegeven volgorde. | string | nee | C​R​U​D |
| subject |  | string | nee | C​R​U​D |
| data |  | object | nee | C​R​U​D |
| dataBase64 |  | string | nee | C​R​U​D |
| dataref | Een referentie naar een locatie waar de data van het EVENT is opgeslagen. | string | nee | C​R​U​D |

## Subscription

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_1.0/doc/objecttype/subscription)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| id |  | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| protocol | Identificatie van het aflever protocol. | string | ja | C​R​U​D |
| sink | Het address waarnaar NOTIFICATIEs afgeleverd worden via het opgegeven protocol. | string | ja | C​R​U​D |
| config | Implementatie specifieke instellingen gebruikt door de abbonements manager om voor het vergaren van notificaties. | object | nee | C​R​U​D |
| source | Bron van dit abonnement. | string | ja | C​R​U​D |
| domain |  | string | nee | C​R​U​D |
| types | Notificaties types relevant voor afleveren voor dit abonnement. | array | nee | C​R​U​D |


* Create, Read, Update, Delete
