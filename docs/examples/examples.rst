.. SPDX-FileCopyrightText: 2017 Mattia Verga <mattia.verga@tiscali.it>
..
.. SPDX-License-Identifier: CC-BY-SA-4.0

##############
Usage examples
##############

Retrieve data for an object
===========================

PyOngc provides data for all NGC and IC objects, plus some other notable objects which may
be of interest for amateur astronomers.

Using ongc library
------------------

The main ongc library provides a convenient method to retrieve a specific object data:

.. code-block:: python

    >>> from pyongc import ongc
    >>> dso = ongc.get('NGC1')
    >>> print(dso)
    NGC0001, Galaxy in Peg

Using `get()` ensure a proper return value when the object identifier is not found in database:

.. code-block:: python

    >>> from pyongc import ongc
    >>> dso = ongc.get('NGC1a')
    >>> print(dso)
    None

If you want to know the exact error, you can try to init the Dso object class directly:

.. code-block:: python

    >>> dso = ongc.Dso('NGC1a')
    Traceback (most recent call last):
      ...
    pyongc.exceptions.ObjectNotFound: Object named NGC0001A not found in the database.

Objects can also be retrieved by their other designations:

.. code-block:: python

    >>> dso = ongc.get('M1')
    >>> print(dso)
    NGC1952, Supernova remnant in Tau

Using CLI
---------

The `ongc` CLI command is a quick shortcut to get object data directly from the terminal:

.. code-block:: bash

    $ ongc view -D NGC1
    +-----------------------------------------------------------------------------+
    | Id: 5596      Name: NGC0001           Type: Galaxy                          |
    | R.A.: 00:07:15.84      Dec.: +27:42:29.1      Constellation: Peg            |
    +-----------------------------------------------------------------------------+
    | Major axis: 1.57'      Minor axis: 1.07'      Position angle: 112°          |
    | B-mag: 13.69   V-mag: 12.93   J-mag: 10.78   H-mag: 10.02   K-mag: 9.76     |
    |                                                                             |
    | Parallax: N/A          Radial velocity: 4536km/s      Redshift: 0.015245    |
    |                                                                             |
    | Proper apparent motion in RA: N/A                                           |
    | Proper apparent motion in Dec: N/A                                          |
    |                                                                             |
    | Surface brightness: 23.13     Hubble classification: Sb                     |
    +-----------------------------------------------------------------------------+
    | Other identifiers:                                                          |
    |    2MASX J00071582+2742291, IRAS 00047+2725, MCG +04-01-025, PGC 000564,    |
    |    UGC 00057                                                                |
    +-----------------------------------------------------------------------------+

Search objects by parameters
============================

Objects can be searched using filters on several properties.

Using ongc library
------------------

.. code-block:: python

    >>> from pyongc import ongc
    >>> obj_list = ongc.listObjects(catalog="NGC", constellation=["Aql", "Boo"], type=["G"], uptovmag=10)
    >>> len(obj_list)
    1
    >>> print(obj_list[0])
    NGC5248, Galaxy in Boo

Using data library
------------------

.. code-block:: python

    >>> from pyongc import data
    >>> obj_list.query('name.str.startswith("NGC")').query('const in ["Aql", "Boo"]').query('vmag<=10')
             name type        ra       dec const  ...  pmdec  radvel  redshift sbrightn hubble
    8397  NGC5248    G  3.567164  0.155075   Boo  ...    NaN  1150.0  0.003843    22.25   SABb

    [1 rows x 24 columns]

Using CLI
---------

.. code-block:: bash

    $ ongc search --catalog=NGC --type=G --constellation=Aql,Boo --uptovmag=10
    NGC5248, Galaxy in Boo

Search objects by position
==========================

Objects can be searched by providing coordinates and search radius.

Using ongc library
------------------

The returned values will be a tuple combining the returned object and the distance
from the coordinates:

.. code-block:: python

    >>> from pyongc import ongc
    >>> obj_list = ongc.nearby('11:08:44 -00:09:01.3')
    >>> len(obj_list)
    3
    >>> print(obj_list[0])
    (<pyongc.ongc.Dso object at 0x...>, 0.1799936868460791)
    >>> print(obj_list[0][0])
    IC0673, Galaxy in Leo

Using CLI
---------

.. code-block:: bash

    $ ongc nearby 11:08:44 -00:09:01.3

    Objects in proximity of 11:08:44 -00:09:01.3 from nearest to farthest:
    0.18° --> IC0673, Galaxy in Leo
    0.74° --> NGC3521, Galaxy in Leo
    0.98° --> IC0671, Galaxy in Leo
    (using a search radius of 60 arcmin)

Search objects in proximity
===========================

Objects can be searched by providing a starting object and a search radius.

Using ongc library
------------------

The returned values will be a tuple combining the returned object and the distance
from the reference object:

.. code-block:: python

    >>> from pyongc import ongc
    >>> dso = ongc.get('ngc521')
    >>> obj_list = ongc.getNeighbors(dso, 15)
    >>> len(obj_list)
    2
    >>> print(obj_list[0])
    (<pyongc.ongc.Dso object at 0x...>, 0.13726168561780452)
    >>> print(obj_list[0][0])
    IC1694, Galaxy in Cet

Using CLI
---------

.. code-block:: bash

    $ ongc neighbors ngc521 --radius 15

    NGC0521 neighbors from nearest to farthest:
    0.14° --> IC1694, Galaxy in Cet
    0.24° --> NGC0533, Galaxy in Cet
    (using a search radius of 15 arcmin)

Get separation between objects
==============================

Using ongc library
------------------

.. code-block:: python

    >>> from pyongc import ongc
    >>> h_per = ongc.get('ngc869')
    >>> chi_per = ongc.get('ngc884')
    >>> ongc.getSeparation(h_per, chi_per)
    (0.483632423459441, 0.8897499999999994, 0.026861111111110007)

Using CLI
---------

.. code-block:: bash

    $ ongc separation ngc869 ngc884
    Apparent angular separation between NGC0869 and NGC0884 is:
    0° 29m 1.08s
