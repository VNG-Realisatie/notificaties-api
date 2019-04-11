===========
Wijzigingen
===========

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
