==============
 Webengine-spv
==============

webengine-spv provides an Importer-based API to fetch/update/reschedule/delete
supervision checks for spvd (the supervision daemon).

License
=======

Webengine-spv is released under the `GNU LGPL 2.1 <http://www.gnu.org/licenses/lgpl-2.1.html>`_.


Build and installation
=======================

Bootstrapping
-------------

Webengine-spv uses autotools for its build system.

If you checked out code from the git repository, you will need
autoconf and automake to generate the configure script and Makefiles.

To generate them, simply run::

    $ autoreconf -fvi

Building
--------

Webengine-spv builds like a typical autotools-based project::

    $ ./configure && make && make install


Development
===========

We use `semantic versioning <http://semver.org/>`_ for
versioning. When working on a development release, we append ``~dev``
to the current version to distinguish released versions from
development ones. This has the advantage of working well with Debian's
version scheme, where ``~`` is considered smaller than everything (so
version 1.10.0 is more up to date than 1.10.0~dev).


Authors
=======

Webengine-spv was started at SmartJog by Thomas Meson in 2009. Various
employees and interns from SmartJog fixed bugs and added features since then.

* Alexandre Bossard
* Anthony Mavic
* Bastien Abadie
* Benoit Mauduit
* Bryann Lamour
* Clément Bœsch
* Gilles Dartiguelongue
* Guillaume Camera
* Marion Leconte
* Mathieu Dupuy
* Matthieu Bouron
* Maxime Mouial
* Nicolas Noirbent
* Philippe Bridant
* Rémi Cardona
* Thomas Meson
* Thomas Souvignet
* Victor Goya
