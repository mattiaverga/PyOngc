
PyOngc
======

A python interface for accessing OpenNGC database data

.. image:: https://img.shields.io/pypi/v/PyOngc.svg
   :target: https://pypi.python.org/pypi/PyOngc
.. image:: https://img.shields.io/pypi/status/PyOngc.svg
.. image:: https://img.shields.io/pypi/pyversions/PyOngc.svg


.. image:: https://github.com/mattiaverga/PyOngc/actions/workflows/python-package.yml/badge.svg?branch=master
   :target: https://github.com/mattiaverga/PyOngc/actions/workflows/python-package.yml
.. image:: https://coveralls.io/repos/github/mattiaverga/PyOngc/badge.svg?branch=master
   :target: https://coveralls.io/github/mattiaverga/PyOngc?branch=master


Description
-----------

PyOngc provides a python module to access astronomical data about NGC
and IC objects.

The data is based on OpenNGC database
https://github.com/mattiaverga/OpenNGC.

It is composed by a python module and a command line interface named
(guess what) ongc, which can be used to quickly see object details or build
object lists based on several parameters.

PyOngc can pass data to PyEphem in a simple way to get
ephemerides of NGC/IC objects: see the documentation about
ongc.xephemFormat method.

Usage
-----

::

        >>> from pyongc import ongc
        >>> DSOobject = ongc.get("NGC7000")
        >>> DSOobject.coords
        array([[20.  , 59.  , 17.14],
               [44.  , 31.  , 43.6 ]])

Object data is easily available from command line also:

::

        $ ongc view NGC7000 --details
        +-----------------------------------------------------------------------------+
        | Id: 13055     Name: NGC7000           Type: HII Ionized region              |
        | R.A.: 20:59:17.14      Dec.: +44:31:43.6      Constellation: Cyg            |
        | Common names:                                                               |
        |    North America Nebula                                                     |
        +-----------------------------------------------------------------------------+
        | Major axis: 120.0'     Minor axis: 30.0'      Position angle: N/A           |
        | B-mag: 4.0     V-mag: N/A     J-mag: N/A     H-mag: N/A     K-mag: N/A      |
        |                                                                             |
        +-----------------------------------------------------------------------------+
        | Other identifiers:                                                          |
        |    C 020, LBN 373                                                           |
        +-----------------------------------------------------------------------------+
        | OpenNGC notes:                                                              |
        |    B-Mag taken from LEDA                                                    |
        +-----------------------------------------------------------------------------+

The full documentation is available at https://pyongc.readthedocs.io/en/latest/.

License
-------

PyOngc is licensed under MIT.
