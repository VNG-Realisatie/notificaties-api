================
Notificaties API
================

:Version: 1.0.0
:Source: https://github.com/VNG-Realisatie/notificaties-api
:Keywords: zaken, zaakgericht werken, GEMMA, notificaties
:PythonVersion: 3.6

|build-status| |black|

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


.. |build-status| image:: https://travis-ci.org/open-zaak/open-notificaties.svg?branch=master
    :alt: Build status
    :target: https://travis-ci.org/open-zaak/open-notificaties

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. _testomgeving: https://notificaties.test.openzaak.nl

Licentie
========

Copyright © VNG Realisatie 2019

Licensed under the EUPL_

.. _EUPL: LICENCE.md
