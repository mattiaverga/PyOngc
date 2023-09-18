.. SPDX-FileCopyrightText: 2017 Mattia Verga <mattia.verga@tiscali.it>
..
.. SPDX-License-Identifier: CC-BY-SA-4.0

Main interface
==============

The `ongc` module is the main interface for retrieving objects data through
Python objects.
It also provides some tools to query the database through several parameters.


Public Classes
^^^^^^^^^^^^^^

.. autoclass:: pyongc.ongc.Dso
   :special-members: __init__, __str__
   :members:

.. autoclass:: pyongc.ongc.DsoEncoder
   :members:


Public Methods
^^^^^^^^^^^^^^

.. autofunction:: pyongc.ongc.get

.. autofunction:: pyongc.ongc.getNeighbors

.. autofunction:: pyongc.ongc.getSeparation

.. autofunction:: pyongc.ongc.listObjects

.. autofunction:: pyongc.ongc.nearby

.. autofunction:: pyongc.ongc.printDetails


Private Methods
^^^^^^^^^^^^^^^

These functions are usually only useful internally.

.. autofunction:: pyongc.ongc._distance

.. autofunction:: pyongc.ongc._limiting_coords

.. autofunction:: pyongc.ongc._queryFetchOne

.. autofunction:: pyongc.ongc._queryFetchMany

.. autofunction:: pyongc.ongc._recognize_name

.. autofunction:: pyongc.ongc._str_to_coords
