================
Notificaties API
================

:Version: 1.0.0
:Source: https://github.com/VNG-Realisatie/notificaties-api
:Keywords: zaken, zaakgericht werken, GEMMA, notificaties

Introductie
===========

De Notificaties API is routeert berichten van componenten (publishers) naar 
andere componenten (subscribers) volgens het publish-subscribe patroon. 
Berichten zijn informatie-arm en bevatten daarom geen inhoudelijke informatie.

Elk component kan een kanaal aanmaken waar het berichten op publiseert met door 
het component gedefinieerde attributen. Op dit kanaal kan een ander component
zich abonneren met filters op de attributen.

Het is aan de subscriber om, bij het ontvangen van een bericht, de bron te 
bevragen naar de informatie waar dan ook de juiste autorisaties voor nodig zijn.

API specificaties
=================

|lint-oas| |generate-sdks| |generate-postman-collection|

==========  ==============  =============================
Versie      Release datum   API specificatie
==========  ==============  =============================
master       n.v.t.         `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/VNG-Realisatie/notificaties-api/master/src/openapi.yaml>`_,
                            `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/VNG-Realisatie/notificaties-api/master/src/openapi.yaml>`_
                            (`verschillen <https://github.com/VNG-Realisatie/notificaties-api/compare/1.0.0..master?diff=split#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
1.0.0       2019-11-18      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/VNG-Realisatie/notificaties-api/1.0.0/src/openapi.yaml>`_,
                            `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/VNG-Realisatie/notificaties-api/1.0.0/src/openapi.yaml>`_
==========  ==============  =============================

Zie ook: `Alle versies en wijzigingen <https://github.com/VNG-Realisatie/notificaties-api/blob/master/CHANGELOG.rst>`_

Ondersteuning
-------------

==========  ==============  ==========================  =================
Versie      Release datum   Einddatum ondersteuning     Documentatie
==========  ==============  ==========================  =================
1.x         2019-11-18      (nog niet bekend)           `Documentatie <https://vng-realisatie.github.io/gemma-zaken/standaard/notificaties/index>`_
==========  ==============  ==========================  =================

Referentie implementatie
========================

|build-status| |coverage| |docker| |black| |python-versions|

Referentieimplementatie van de Notificaties API. Ook wel
Notificatierouteringscomponent (NRC) genoemd.

Ontwikkeld door `Maykin Media B.V. <https://www.maykinmedia.nl>`_ in opdracht
van VNG Realisatie.

Deze referentieimplementatie toont aan dat de API specificatie voor de
Notificaties API implementeerbaar is, en vormt een voorbeeld voor andere
implementaties indien ergens twijfel bestaat.

Deze component heeft ook een `demo omgeving`_ waar leveranciers tegenaan kunnen
testen.

Links
=====

* Deze API is onderdeel van de `VNG standaard "API's voor Zaakgericht werken" <https://github.com/VNG-Realisatie/gemma-zaken>`_.
* Lees de `functionele specificatie <https://vng-realisatie.github.io/gemma-zaken/standaard/notificaties/index>`_ bij de API specificatie.
* Bekijk de `demo omgeving`_ met de laatst gepubliceerde versie.
* Bekijk de `test omgeving <https://notificaties-api.test.vng.cloud/>`_ met de laatste ontwikkel versie.
* Rapporteer `issues <https://github.com/VNG-Realisatie/gemma-zaken/issues>`_ bij vragen, fouten of wensen.
* Bekijk de `code <https://github.com/VNG-Realisatie/notificaties-api/>`_ van de referentie implementatie.

.. _`demo omgeving`: https://notificaties-api.vng.cloud/

Licentie
========

Copyright © VNG Realisatie 2018 - 2020

Licensed under the EUPL_

.. _EUPL: LICENCE.md

.. |build-status| image:: https://travis-ci.org/VNG-Realisatie/notificaties-api.svg?branch=master
    :alt: Build status
    :target: https://travis-ci.org/VNG-Realisatie/notificaties-api

.. |requirements| image:: https://requires.io/github/VNG-Realisatie/notificaties-api/requirements.svg?branch=master
     :alt: Requirements status

.. |coverage| image:: https://codecov.io/github/VNG-Realisatie/notificaties-api/branch/master/graphs/badge.svg?branch=master
    :alt: Coverage
    :target: https://codecov.io/gh/VNG-Realisatie/notificaties-api

.. |docker| image:: https://img.shields.io/badge/docker-latest-blue.svg
    :alt: Docker image
    :target: https://hub.docker.com/r/vngr/notificaties-api

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :alt: Code style
    :target: https://github.com/psf/black

.. |python-versions| image:: https://img.shields.io/badge/python-3.6%2B-blue.svg
    :alt: Supported Python version

.. |lint-oas| image:: https://github.com/VNG-Realisatie/notificaties-api/workflows/lint-oas/badge.svg
    :alt: Lint OAS
    :target: https://github.com/VNG-Realisatie/notificaties-api/actions?query=workflow%3Alint-oas

.. |generate-sdks| image:: https://github.com/VNG-Realisatie/notificaties-api/workflows/generate-sdks/badge.svg
    :alt: Generate SDKs
    :target: https://github.com/VNG-Realisatie/notificaties-api/actions?query=workflow%3Agenerate-sdks

.. |generate-postman-collection| image:: https://github.com/VNG-Realisatie/notificaties-api/workflows/generate-postman-collection/badge.svg
    :alt: Generate Postman collection
    :target: https://github.com/VNG-Realisatie/notificaties-api/actions?query=workflow%3Agenerate-postman-collection
