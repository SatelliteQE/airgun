AirGun
======

AirGun is a Python library which is build over `Widgetastic`_ and `navmazing`_
to make Satellite 6 UI testing easier.

AirGun is written in Python 3 and do not plan to support Python 2. AirGun
supports Satellite 6.4 and above and Foreman 1.17 and above (with vertical
navigation).

This page provides a summary of information about AirGun.

.. contents::

More in-depth coverage is provided in other sections.

.. toctree::
    :maxdepth: 1

    build-docs
    api/index
    examples


Concepts
--------

Besides code which implements Widgetastic and navmazing functionality, two
basic concepts used to abstract Satellite/Foreman UI functionality are Views
and Entities.

**View** is part of page containing widgets, it describes appearance of the
page. Here all the nasty XPaths goes, but please create Foreman or Katello
pull requests for `id=...` additions where reasonable, as generally XPaths
are too fragile.

**Entity** is a functional side of application (Satellite or Foreman in our
case) for some object in it. It defines actions you can do with the object.
This is the API that end tests uses.

AirGun adds bunch of **widgets** (which are specific to Satellite / Foreman
web UI) to these defined by Widgetastic (like generic `Text`). Widgets allows
you to interact with various UI elements and are used in views.

And finally tests. Tests are not part of AirGun repository. You can
contribute tests to the Robottelo (currently only in abalakh's fork, `branch
airgun_poc`_ (see "Quick start guide" below).


Quick start guide
-----------------

1. Clone Robottelo branch which supports airgun:

.. code-block:: bash

    git clone -b airgun_poc --single-branch https://github.com/abalakh/robottelo.git

2. Install requirements

.. code-block:: bash

    cd robottelo && pip install -r requirements.txt

3. Create `robottelo.properties` file and fill it with your values (your may
reuse already existing properties file since no changes were introduced there)

.. code-block:: bash

    cp robottelo.properties.sample robottelo.properties
    vim robottelo.properties

4. Run airgun tests from Robottelo's ``tests/foreman/ui_airgun/`` folder

.. code-block:: bash

    pytest tests/foreman/ui_airgun/test_architecture.py


Contributing
------------

Good practice when working with Python project as AirGun is to work in
Python's virtual environments. To initiate and activate them before running
`pip ...` commands run:

.. code-block:: bash

    virtualenv venv   # on Fedora you might need to use `virtualenv-3` if you have Python 2 as a default on your system
    source venv/bin/activate

If you are about to start contributing, please follow `GitHub flow`_.

For a new-comer, we have issues tagged with "`good first issue`_" so that
might be place where you can start?

When testing your AirGun code using Robottelo tests, I have used following
ugly trick to have mine current development version of AirGun available in
Robottelo virtual environment:

.. code-block:: bash

    mv venv/lib/python3.6/site-packages/airgun{,ORIG}
    ln -s ../airgun/airgun/ venv/lib/python3.6/site-packages/airgun   # depends where you have airgun checked out

When you are running your tests locally, you (currently) need Chrome browser
installed and `chromedriver`_ binary available somewhere in your PATH (in
your robottelo checkout): download it, unzip it and put e.g. into (if you
are using virtual environments) `venv/bin/`.


.. _Widgetastic: https://github.com/RedHatQE/widgetastic.core
.. _navmazing: https://github.com/RedhatQE/navmazing/
.. _branch airgun_poc: https://github.com/abalakh/robottelo/tree/airgun_poc/tests/foreman/ui_airgun
.. _GitHub flow: https://help.github.com/articles/github-flow/
.. _good first issue: https://github.com/SatelliteQE/airgun/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22
.. _chromedriver: https://sites.google.com/a/chromium.org/chromedriver/downloads
