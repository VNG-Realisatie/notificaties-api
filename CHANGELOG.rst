=======
Changes
=======

1.1.0 (2020-03-16)
==================

Feature and small improvements release.

.. note:: The API remains unchanged.

* Removed unnecessary sections in documentation
* Updated deployment examples
* Tweak deployment to not conflict (or at least less likely :-) ) with Open Zaak install
  Open Zaak and Open Notificaties on the same machine are definitely supported
* Added support for ADFS Single Sign On (disabled by default)
* Added documentation build to CI

1.0.0 final (2020-02-07)
========================

🎉 First stable release of Open Notificaties.

Features:

* Notificaties API implementation
* Tested with Open Zaak integration
* Admin interface to view data created via the APIs
* Scalable notification delivery workers
* `NLX`_ ready (can be used with NLX)
* Documentation on https://open-notificaties.readthedocs.io/
* Deployable on Kubernetes, single server and as VMware appliance
* Automated test suite
* Automated deployment

.. _NLX: https://nlx.io/
