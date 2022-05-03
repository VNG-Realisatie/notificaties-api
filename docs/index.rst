.. _index:

===============================
Notifications API documentation
===============================

Welcome to the developer documentation for the Notifications API.

:Version: 1.0.0-rc1
:Source: https://github.com/VNG-Realisatie/gemma-notificatiecomponent
:Keywords: zaken, zaakgericht werken, GEMMA, notificaties
:PythonVersion: 3.9

|build-status|

The purpose of this documentation is two-fold:

* document the technicalities of this reference implementation of the
  VNG `notifications API`_
* provide more context and guidelines

Introduction
============

In the `Common Ground`_ vision, copying data around between services is a thing
of the past. Providers are responsible for maintaining their data, while
consumers directly retrieve information from the providers. However, various
parties may be interested in events related to that information, such as
mutations.

The 'Notifications API' provides an interface for providers to create event
channels, broadcast events to said channels and for interested parties to
subscribe to these events.

Documentation
=============

.. toctree::
    :maxdepth: 3
    :caption: Contents:

    contents/for-contributors/index
    changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _notifications API: https://zaakgerichtwerken.vng.cloud/standaard/notificaties/index

.. _Common Ground: https://commonground.nl/

.. |build-status| image:: http://jenkins.nlx.io/buildStatus/icon?job=gemma-notificatiecomponent-stable
    :alt: Build status
    :target: http://jenkins.nlx.io/job/gemma-notificatiecomponent-stable

.. |requirements| image:: https://requires.io/github/VNG-Realisatie/gemma-notificatiecomponent/requirements.svg?branch=master
     :target: https://requires.io/github/VNG-Realisatie/gemma-notificatiecomponent/requirements/?branch=master
     :alt: Requirements status
