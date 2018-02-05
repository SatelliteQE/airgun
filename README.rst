Airgun
======

Airgun is a Python library which is build over `Widgetastic`_ and `navmazing`_
to make Satellite 6 UI testing easier.

Quick start guide
-----------------

1. Clone robottelo branch which supports airgun:

.. code-block:: bash

    git clone -b airgun_poc --single-branch https://github.com/abalakh/robottelo.git

2. Install requirements

.. code-block:: bash

    cd robottelo && pip install -r requirements.txt

3. Create robottelo.properties file and fill it with your values (your may
reuse already existing properties file since no changes were introduced there)

.. code-block:: bash

    cp robottelo.properties.example robottelo.properties
    vim robottelo.properties

4. Run airgun tests from robottelo's ``tests/foreman/ui_airgun/`` folder

.. code-block:: bash

    pytest tests/foreman/ui_airgun/test_architecture.py

.. _Widgetastic: https://github.com/RedHatQE/widgetastic.core
.. _navmazing: https://github.com/RedhatQE/navmazing/
