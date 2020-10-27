================
Notificaties API
================

:Version: 1.0.0
:Source: https://github.com/VNG-Realisatie/notificaties-api
:Keywords: zaken, zaakgericht werken, GEMMA, notificaties
:PythonVersion: 3.6

|build-status| |black| |lint-oas| |generate-sdks| |generate-postman-collection|

Referentieimplementatie van de notificatierouteringcomponent (NRC).

Inleiding
=========

De Notificaties API is een referentieimplementatie van hoe
notificaties afgehandeld worden binnen de gemma-architectuur en in het
bijzonder het zaakgericht werken.

Deze component heeft ook een `testomgeving`_ waar leveranciers tegenaan kunnen
testen.

Documentatie
============

Zie ``INSTALL.rst`` voor installatieinstructies, beschikbare instellingen en
commando's.

Indien je actief gaat ontwikkelen aan deze component raden we aan om niet van
Docker gebruik te maken. Indien je deze component als black-box wil gebruiken,
raden we aan om net wel van Docker gebruik te maken.

Referenties
===========

* `Issues <https://github.com/VNG-Realisatie/notificaties-api/issues>`_
* `Code <https://github.com/VNG-Realisatie/notificaties-api>`_


.. |build-status| image:: https://travis-ci.org/VNG-Realisatie/notificaties-api.svg?branch=develop
    :alt: Build status
    :target: https://travis-ci.org/VNG-Realisatie/notificaties-api

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. |lint-oas| image:: https://github.com/VNG-Realisatie/notificaties-api/workflows/lint-oas/badge.svg
    :alt: Lint OAS
    :target: https://github.com/VNG-Realisatie/notificaties-api/actions?query=workflow%3Alint-oas

.. |generate-sdks| image:: https://github.com/VNG-Realisatie/notificaties-api/workflows/generate-sdks/badge.svg
    :alt: Generate SDKs
    :target: https://github.com/VNG-Realisatie/notificaties-api/actions?query=workflow%3Agenerate-sdks

.. |generate-postman-collection| image:: https://github.com/VNG-Realisatie/notificaties-api/workflows/generate-postman-collection/badge.svg
    :alt: Generate Postman collection
    :target: https://github.com/VNG-Realisatie/notificaties-api/actions?query=workflow%3Agenerate-postman-collection

.. _testomgeving: https://notificaties-api.vng.cloud

Licentie
========

Copyright © VNG Realisatie 2019

Licensed under the EUPL_

.. _EUPL: LICENCE.md
