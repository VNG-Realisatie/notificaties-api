# Resources

Dit document beschrijft de (RGBZ-)objecttypen die als resources ontsloten
worden met de beschikbare attributen.


## Domain

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_1.0/doc/objecttype/domain)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| name | Name of the domain. | string | ja | C​R​U​D |
| documentationLink | Link to human readable information about the domain and its notifications. | string | nee | C​R​U​D |
| filterAttributes | Filter attributes offered by the domain. | array | nee | C​R​U​D |
| url | URL-referentie naar dit object. Dit is de unieke identificatie en locatie van dit object. | string | nee | ~~C~~​R​~~U~~​~~D~~ |

## Event

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_1.0/doc/objecttype/event)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| id | Identifies the event. Producers MUST ensure that source + id is unique for each distinct event. SHOULD be a UUID. | string | ja | C​R​U​D |
| specversion | The version of the CloudEvents specification which the event uses. Compliant event producers MUST use a value of 1.0 when referring to this version of the specification. | string | ja | C​R​U​D |
| source | Identifies the context in which an event happened. SHOULD be a URN notation with &#x27;nld&#x27; as namespace identifier. SHOULD contain consecutive a unique identifier of the organization that publishes the event followed by the source system that publishes the event. Involved organizations SHOULD agree on how organizations and systems are uniquely identified (e.g. via the use of OIN, KVK-nummer or eIDAS legal identifier for organization identification);. | string | ja | C​R​U​D |
| domain | Name of the domain to which the event belongs. Can be seen as the namespace of the event.(This attribute is not listed in the GOV NL profile for CloudEvents). | string | ja | C​R​U​D |
| type | Beschrijft het type EVENT afkomstig van het specifieke DOMAIN.This attribute contains a value describing the type of event. Type SHOULD start with the domain followed by the name of the event. Events SHOULD be expressed in the past tense. If subtypes are required those SHOULD be expressed using a dot &#x27;.&#x27; between the super and subtype(s). The type MAY contain version information. Version information SHOULD be appended at the end of the string. | string | ja | C​R​U​D |
| time | Timestamp of the event. SHOULD be the timestamp the event was registered in the source system and NOT the time the event occurred in reality. The exact meaning of time MUST be clearly documented. | string | nee | C​R​U​D |
| subscription | Usually empty. Only used in situations where notificationservices are chained. For example notificationservice2 (ns2) is subscribed to notifcationservice1 (ns1). When ns1 sends an event to ns2 this attribute SHOULD contain the subscription id of the subscription that ns1 has on ns2 (that was resposible for receiving the event). Note this attribute is overwritten when the event is passed through to a client. It will be set to the value of the subscription id of the subscription of the client. | string | nee | C​R​U​D |
| subscriberReference | Usually empty. Only used in situations where notificationservices are chained. For example notificationservice2 (ns2) is subscribed to notifcationservice1 (ns1). When ns1 sends an event to ns2 this attribute COULD contain the subscriberReference the was specified when ns2 subscribed to ns1. Note this attribute is overwritten when the event is passed through to a client. It will be set to the value of the subscriberReference of the subscription of the client (when specified by the client). | string | nee | C​R​U​D |
| datacontenttype | Content type of data value. In this version of the API the value MUST be &#x27;application/json&#x27;. In future versions of the API other values such as described in RFC 2046 MAY be used. | string | nee | C​R​U​D |
| dataschema | Identifies the schema that data adheres to. | string | nee | C​R​U​D |
| sequence | Value expressing the relative order of the event. This enables interpretation of data supercedence. | string | nee | C​R​U​D |
| sequencetype | Specifies the semantics of the sequence attribute. (Currently limited to the value INTEGER). | string | nee | C​R​U​D |
| subject | Included to be compatible with CloudEvents specification. The GOV NL profile states &#x27;Decision on whether or not to use the attribute and/or the exact interpretation is postponed. To be determined partly on the basis of future agreements about subscription and filtering.&#x27; | string | nee | C​R​U​D |
| data |  | object | nee | C​R​U​D |
| data_base64 | The presence of the data_base64 member clearly indicates that the value is a Base64 encoded binary data, which the serializer MUST decode into a binary runtime data type. | string | nee | C​R​U​D |
| dataref | A reference to a location where the event payload is stored. If both the data attribute and the dataref attribute are specified their contents MUST be identical. | string | nee | C​R​U​D |

## Subscription

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_1.0/doc/objecttype/subscription)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| id | UUID of the subscription. | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| protocol | Identifier of a delivery protocol. | string | ja | C​R​U​D |
| sink | The address to which events shall be delivered using the selected protocol. | string | ja | C​R​U​D |
| config | Implementation-specific configuration parameters needed by the subscription manager for acquiring events. | object | nee | C​R​U​D |
| source | Source to which the subscription applies. May be implied by the request address. | string | nee | C​R​U​D |
| domain | Domain to which the subscription applies. | string | nee | C​R​U​D |
| types | CloudEvent types eligible to be delivered by this subscription. | array | nee | C​R​U​D |
| subscriberReference | Events that are send to the subscriber will contain this reference. The subscriber can use the reference for internal routing of the event. | string | nee | C​R​U​D |
| filters | This filter evaluates to &#x27;true&#x27; if all contained filters are &#x27;true&#x27;. | object | nee | C​R​U​D |


* Create, Read, Update, Delete
