===========
Wijzigingen
===========

0.7.1 (2019-07-01)
==================

Fixed bug in docker start script preventing fixtures from being loaded.

0.7.0 (2019-06-19)
==================

First release towards RC

* Bumped to latest security releases of dependencies
* Translated API docs
* Fixed display of message-delivery responses (status code from string to int)
* Added fixture loading to the container start script

0.6.3 (2019-05-22)
==================

Debugging

* Added notification webhook
* Set up view-config page

0.6.2 (2019-05-22)
==================

Fixed notification handler

0.6.1 (2019-05-22)
==================

Patched webhook subscription

0.6.0 (2019-05-22)
==================

Migrate to authorizations V2 setup - breaking change

* Authorizations are now checked against an authorization component (AC)
* Scope labels renamed for better consistency
* Refactored some code with existing stuff from vng-api-common
* updated ``invalid-params`` to ``invalidParams`` in error messages, following
  the KP-API strategy
* Bumped dependencies to latest security releases

0.5.0 (2019-04-16)
==================

API-lab release

* Updated Kubernetes config samples
* Updated to latest vng-api-common
* Renamed from NC to NRC

0.4.0 (2019-04-11)
==================

* added robustness in delivering messages
* log responses of message deliveries
* added auth checks so that you an only modify/delete own subscriptions
  ("abonnementen")
* added a simple UI to view notifications log
* restyled using Bootstrap with generic styles from vng-api-common

Breaking changes
----------------

* flattened the structure of ``filters`` and ``kenmerken``. Instead of a list
  of objects with a single key-value pair, it is now an object with (possibly)
  multiple key-value pairs.
* made message delivery async by using celery. Celery now needs to run to
  actually deliver messages. See ``docker-compose.yml`` for the container
  setup.

0.3.0 (2019-03-27)
==================

Added the ``filters`` array to the ``kanaal`` resource.

0.2.0 (2019-03-25)
==================

Added a filter param 'naam' on the Kanaal list endpoint

0.1.0 (2019-03-22)
==================

Initial release

Features:

* API endpoints to manage subscriptions ('abonnementen', CRUD)
* API endpoints to manage exchanges ('kanalen', CR)
* API endpoint to send notifications to
* docker-compose with RabbitMQ
