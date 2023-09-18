.. SPDX-FileCopyrightText: 2017 Mattia Verga <mattia.verga@tiscali.it>
..
.. SPDX-License-Identifier: CC-BY-SA-4.0

=================
The CLI interface
=================

Synopsis
========

``ongc`` COMMAND [OPTIONS] [ARGS]...


Description
===========

``ongc`` is the command line interface to used to browse ONGC database data. It can be used
to query data about an object or to build up lists based on some parameters.


Commands
========

Nearby
------

The ``nearby`` command allows to list objects in proximity of given J2000 coordinates.
If the ouput exceed 20 objects, the user can choose to view the list in a pager.

The coordinates must be expressed in the form `HH:MM:SS(.SS) +/-DD:MM:SS(.S)`

``ongc nearby [options] RA DEC``

    ``RA``

        Right Ascension in the form `HH:MM:SS(.SS)`

    ``DEC``

        Declination in the form `+/-DD:MM:SS(.S)`

    ``--radius INTEGER``

        It's the radius ot the search, expressed in arcmin. If it's not provided, the search is
        made with a default value of 60'.

    ``--catalog [all|NGC|IC]``

        Allows to list only objects from NGC or IC catalog. By default the search will ouput
        all objects.

Neighbors
---------

The ``neighbors`` command allows to list objects in proximity of another object.
If the ouput exceed 20 objects, the user can choose to view the list in a pager.

``ongc neighbors [options] NAME``

    ``NAME``

        The identifier of the object. It can be the main identifier (NGC or IC id) or one of
        the alternative identifier.

    ``--radius INTEGER``

        It's the radius ot the search, expressed in arcmin. If it's not provided, the search is
        made with a default value of 30'.

    ``--catalog [all|NGC|IC]``

        Allows to list only objects from NGC or IC catalog. By default the search will ouput
        all objects.

Search
------

The ``search`` command allows to build up a list of objects with specific parameters. The
different options can be combined to perform a very granular search.

If the ouput exceed 20 objects, the user can choose to view the list in a pager.

``ongc search [options]``

    ``--catalog [all|NGC|IC]``

        Allows to list only objects from NGC or IC catalog. By default the search will ouput
        all objects.

    ``--type TEXT``

        Allows to list only objects of specific kinds. It accepts multiple comma separated values
        of the object types listed in the 
        `OpenNGC guide <https://github.com/mattiaverga/OpenNGC/blob/master/NGC_guide.txt>`_.

    ``--constellation TEXT``

        Allows to list only objects within some constellations boundaries. It accepts multiple comma
        separated values. Use IAU 3-letter form.

    ``--minsize FLOAT``

        Allows to list only objects with a major axis greater or equal than the specified value
        expressed in arcmin.

    ``--maxsize FLOAT``

        Allows to list only objects with a major axis lower than the specified value
        expressed in arcmin.

        It will also include all objects with an unknown major axis value.

    ``--uptobmag FLOAT``

        Allows to list only objects with B-Mag brighter than the specified value.

    ``--uptovmag FLOAT``

        Allows to list only objects with V-Mag brighter than the specified value.

    ``--minra TEXT``

        Allows to list only objects with a Right Ascension greater than the specified value.
        It accepts an input in the form `HH:MM:SS(.SS)`

    ``--maxra TEXT``

        Allows to list only objects with a Right Ascension lower than the specified value.
        It accepts an input in the form `HH:MM:SS(.SS)`

    ``--mindec TEXT``

        Allows to list only objects with a Declination greater than the specified value.
        It accepts an input in the form `+/-DD:MM:SS(.S)`

    ``--maxdec TEXT``

        Allows to list only objects with a Declination lower than the specified value.
        It accepts an input in the form `+/-DD:MM:SS(.S)`

    ``-n, --named TEXT``

        Allows to search an object by its common name (or part of it).

    ``-N, --withname``

        Allows to list only objects with a common name.

    ``-O, --out_file FILENAME``

        Outputs the results to a file rather than to the terminal.

    ``-I, --include_fields field_1,field_2,...,field_n``

        Combined with `-O` it will produce a csv file with the requested fields added to
        the results output. The `name` field is always included.
        Other available fields are: `type | ra | dec | const | majax | minax | pa |
        bmag | vmag | jmag | hmag | kmag | sbrightn | hubble | parallax | pmra | pmdec
        | radvel | redshift | cstarumag | cstarbmag | cstarvmag | messier | ngc | ic |
        cstarnames | identifiers | commonnames | nednotes | ongnotes`.

Separation
----------

The ``separation`` command returns the apparent angular separation between two objects.

``ongc separation OBJ1 OBJ2``

    ``OBJ1``

        The identifier of the object. It can be the main identifier (NGC or IC id) or one of
        the alternative identifier.

    ``OBJ2``

        The identifier of the object. It can be the main identifier (NGC or IC id) or one of
        the alternative identifier.

Stats
-----

The ``stats`` command shows some information about the database in use.

``ongc stats``

View
----

The ``view`` command allows to gather information about a specific object.

``ongc view [options] NAME``

    Without options, prints a brief description of the object composed by the main identifier
    used in ONGC database, the object type and the constellation where the object is located.

    ``NAME``

        The identifier of the object. It can be the main identifier (NGC or IC id) or one of
        the alternative identifier.

    ``-D, --details``

        Prints all the available information about the object.

        The output is rendered in a table suited to be viewed in a 80cols terminal.


Help
====

If you find bugs in ongc (or in the man page), please feel free to file a bug report or a pull
request::

    https://github.com/mattiaverga/PyOngc

