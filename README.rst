.. SPDX-FileCopyrightText: 2017 Mattia Verga <mattia.verga@tiscali.it>
..
.. SPDX-License-Identifier: CC-BY-SA-4.0

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
        | Id: 13067     Name: NGC7000           Type: HII Ionized region              |
        | R.A.: 20:59:17.14      Dec.: +44:31:43.6      Constellation: Cyg            |
        | Common names:                                                               |
        |    North America Nebula                                                     |
        +-----------------------------------------------------------------------------+
        | Major axis: 120.0'     Minor axis: 30.0'      Position angle: N/A           |
        | B-mag: 4.0     V-mag: N/A     J-mag: N/A     H-mag: N/A     K-mag: N/A      |
        |                                                                             |
        | Parallax: N/A          Radial velocity: N/A           Redshift: N/A         |
        |                                                                             |
        | Proper apparent motion in RA: N/A                                           |
        | Proper apparent motion in Dec: N/A                                          |
        |                                                                             |
        +-----------------------------------------------------------------------------+
        | Other identifiers:                                                          |
        |    C 020, LBN 373                                                           |
        +-----------------------------------------------------------------------------+

Additionally, the available data can be manipulated through Pandas:

::

        >>> from pyongc import data
        >>> data.clusters(globular=True, open=False)
                name type        ra       dec const  ...  parallax  pmra  pmdec radvel  redshift
        0     IC1257  GCl  4.569009 -0.123798   Oph  ...       NaN   NaN    NaN    NaN       NaN
        1     IC1276  GCl  4.759242 -0.125796   Se2  ...    0.1100 -2.47  -4.41  155.0  0.000517
        2     IC2134  GCl  1.409778 -1.316796   Men  ...       NaN   NaN    NaN    NaN       NaN
        3     IC2140  GCl  1.454580 -1.315548   Men  ...       NaN   NaN    NaN    NaN       NaN
        4     IC2146  GCl  1.473853 -1.305213   Men  ...       NaN   NaN    NaN  226.0  0.000755
        ..       ...  ...       ...       ...   ...  ...       ...   ...    ...    ...       ...
        199  NGC7006  GCl  5.504278  0.282526   Del  ...       NaN -0.08  -0.61 -383.0 -0.001278
        200  NGC7078  GCl  5.628569  0.212351   Peg  ...    0.0522 -0.63  -3.80 -107.0 -0.000356
        201  NGC7089  GCl  5.643741 -0.014369   Aqr  ...    0.0612  3.51  -2.16   -4.0 -0.000012
        202  NGC7099  GCl  5.673921 -0.404551   Cap  ...    0.0676 -0.73  -7.24 -185.0 -0.000618
        203  NGC7492  GCl  6.058233 -0.272472   Aqr  ...    0.0528  0.76  -2.30 -177.0 -0.000589

        [204 rows x 22 columns]

The full documentation is available at https://pyongc.readthedocs.io/en/latest/.

License
-------

PyOngc code is licensed under MIT. The documentation and the database from OpenNGC are
licensed under CC-BY-SA-4.0.
