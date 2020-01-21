.. _performance_scenarios:

=====================
Measuring performance
=====================

Goal
====

The purpose of performance measurements is to gain insight into the relationships
between system requirements, number of users and response times of the API's. From these
relationships we can draw up the minimum system requirements, depending on the number
of users, on which the API's still perform acceptable.

A standardized performance measurement also provides insight into which effect various
optimizations have.

Technical test scenarios
========================

There's basically just one API-call that will be called often and that's to send a
notification. The other API-calls are neglible. The API-call (request) is measured to
gain insights in the technical performance.

**Notificaties API**

1. Create NOTIFICATIE (``POST /api/v1/notificaties``)

Test specification
------------------

Using scenarios
~~~~~~~~~~~~~~~

A scenario in this test specification is equal to an API-call (request). Each API
resource is continuously without any delay, or *waiting time*, between each request.
This way, we can determine the maximum number of requests per second and average
response times.

Virtual users
~~~~~~~~~~~~~

We test with an increasing number of virtual users, from 1 to 100, that concurrently
execute the test scenarios. A virtual user is technically a script that executes the
different scenarios one after another. This way, we see the number of virtual users
that concurrently access the API's and its impact on performance.

Testdata
~~~~~~~~

There's not test data involved.
