# PyOngc
A python interface for accessing OpenNGC database data

## Description
PyOngc provides a python module to access astronomical data about NGC and
IC objects.

The data is based on OpenNGC database
<https://github.com/mattiaverga/OpenNGC>.

It is composed by a main module and a command line utility named
ongcbrowse which can be used to print object details in a terminal.

PyOngc data can provide data to PyEphem in a simple way to get ephemerides
of NGC/IC objects. See the documentation about ongc.xephemFormat method.

## Usage
        >>> from pyongc import ongc
        >>> DSOobject = ongc.Dso("NGC7000")
        >>> DSOobject.getCoords()
        ((20, 59, 17.14), ('+', 44, 31, 43.6))

Object data is easily available from command line also:

        $ ongcbrowse --details NGC7000
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
        |    C20, LBN 373                                                             |
        +-----------------------------------------------------------------------------+
        | OpenNGC notes:                                                              |
        |    B-Mag taken from LEDA                                                    |
        +-----------------------------------------------------------------------------+

## License
PyOngc is licensed under MIT.
