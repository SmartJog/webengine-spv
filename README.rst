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

* Alexandre Bossard <alexandre.bossard@smartjog.com>
* Anthony Mavic <anthony.mavic@smartjog.com>
* Bastien Abadie <bastien.abadie@smartjog.com>
* Benoit Mauduit <benoit.mauduit@smartjog.com>
* Bryann Lamour <bryann.lamour@smartjog.com>
* Clément Bœsch <clement.boesch@smartjog.com>
* Gilles Dartiguelongue <gilles.dartiguelongue@smartjog.com>
* Guillaume Camera <guillaume.camera@smartjog.com>
* Marion Leconte <marion.leconte@smartjog.com>
* Mathieu Dupuy <mathieu.dupuy@smartjog.com>
* Matthieu Bouron <matthieu.bouron@smartjog.com>
* Maxime Mouial <maxime.mouial@smartjog.com>
* Nicolas Noirbent <nicolas.noirbent@smartjog.com>
* Philippe Bridant <philippe.bridant@smartjog.com>
* Rémi Cardona <remi.cardona@smartjog.com>
* Thomas Meson <thomas.meson@smartjog.com>
* Thomas Souvignet <thomas.souvignet@smartjog.com>
* Victor Goya <victor.goya@smartjog.com>
