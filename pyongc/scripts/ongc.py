#!/usr/bin/python
# -*- coding:utf-8 -*-
#
#
# MIT License
#
# Copyright (c) 2017 Mattia Verga <mattia.verga@tiscali.it>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#

"""A Command Line Interface to query OpenNGC database.

    Usage: ongc [OPTIONS] COMMAND [ARGS]...
"""

from pyongc import ongc
import click

from os import environ

# Make sure Less pager will properly display utf-8 characters
environ["LESSCHARSET"] = 'utf-8'


@click.group()
def cli():
    """A Command Line Interface to query OpenNGC database."""
    pass


@cli.command()
@click.argument('name')
@click.option('--details', '-D', is_flag=True,
              help='Show detailed information or just summary')
def view(name, details):
    """Print out object information."""
    try:
        if details:
            click.echo(ongc.printDetails(ongc.Dso(name)))
        else:
            click.secho(str(ongc.Dso(name)), bold=True)
    except Exception as e:
        click.echo(click.style('ERROR: ', fg='red', bold=True) + str(e))


@cli.command()
def stats():
    """Show database statistics."""
    try:
        informations = ongc.stats()
        click.echo(click.style('\nPyONGC version: ', bold=True)
                   + ongc.__version__)
        click.echo(click.style('Database version: ', bold=True)
                   + str(informations[1]))
        click.echo(click.style('Total number of objects in database: ', bold=True)
                   + str(informations[2]))
        click.secho('Object types statistics:', bold=True)
        for objType, objCount in informations[3]:
            click.echo('\t{:29}'.format(objType) + '-> ' + str(objCount))
    except Exception as e:
        click.echo(click.style('ERROR: ', fg='red', bold=True) + str(e))


@cli.command()
@click.argument('name')
@click.option('--radius', default=30, show_default=True,
              help='Maximum separation from the starting DSO (arcmin)')
@click.option('--catalog', type=click.Choice(['all', 'NGC', 'IC']),
              default='all', show_default=True,
              help='Search only for NGC or IC objects')
def neighbors(name, radius, catalog):
    """List objects in proximity of another DSO."""
    try:
        start_obj = ongc.Dso(name)
        object_list = ongc.getNeighbors(start_obj, radius, catalog)
        if len(object_list) == 0:
            click.secho('\nNo objects found within search radius!', bold=True)
            return
        if len(object_list) > 20:
            if click.confirm(click.style('WARNING: ', fg='yellow', bold=True)
                             + 'the result list is long. Do you want to see it via a pager?'):
                click.echo_via_pager('\n'.join('{:.2f}° --> {}'.format(dso[1], dso[0])
                                               for dso in object_list))
                return

        click.secho('\n' + start_obj.getName() + ' neighbors from nearest to farthest:', bold=True)
        for dso in object_list:
            click.echo('{:.2f}° --> {}'.format(dso[1], dso[0]))
        if catalog != 'all':
            search_filter = ' and showing ' + catalog + ' objects only'
        else:
            search_filter = ''
        click.secho('(using a search radius of {} arcmin{})\n'.format(radius, search_filter),
                    fg='cyan')
    except Exception as e:
        click.echo(click.style('ERROR: ', fg='red', bold=True) + str(e))


@cli.command()
@click.argument('obj1')
@click.argument('obj2')
def separation(obj1, obj2):
    """Return the apparent angular separation between two objects."""
    try:
        first = ongc.Dso(obj1)
        second = ongc.Dso(obj2)
        click.echo('Apparent angular separation between '
                   + click.style(first.getName(), fg='cyan')
                   + ' and '
                   + click.style(second.getName(), fg='cyan')
                   + ' is:')
        click.secho(ongc.getSeparation(obj1, obj2, style="text"), bold=True)
    except Exception as e:
        click.echo(click.style('ERROR: ', fg='red', bold=True) + str(e))


@cli.command()
@click.option('--catalog', type=click.Choice(['NGC', 'IC', 'M']),
              help='List only objects from specific catalog')
@click.option('--type',
              help='List only objects of specific type. See OpenNGC types list.')
@click.option('--constellation',
              help='List only objects in specific constellation.')
@click.option('--minsize', type=float,
              help='List only objects with major axis >= minsize (arcmin)')
@click.option('--maxsize', type=float,
              help=('List only objects with major axis < maxsize (arcmin) '
                    'or when major axis is not known')
              )
@click.option('--uptobmag', type=float,
              help='List only objects with B-Mag brighter than value')
@click.option('--uptovmag', type=float,
              help='List only objects with V-Mag brighter than value')
@click.option('--named', '-N', 'withname', is_flag=True, help='List only objects with common name')
@click.option('--out_file', '-O', type=click.File('w'),
              help='Output results to text file')
def search(out_file, **kwargs):
    """Search in the database for objects with given parameters."""
    try:
        object_list = ongc.listObjects(**{k: v for k, v in kwargs.items() if (v is not None
                                                                              and v is not False)})
        if len(object_list) == 0:
            click.secho('\nNo objects found with such parameters!', bold=True)
            return
        if out_file is not None:
            out_file.write('\n'.join(str(dso) for dso in object_list))
            out_file.flush()
        else:
            if len(object_list) > 20:
                if click.confirm(click.style('WARNING: ', fg='yellow', bold=True)
                                 + 'the result list is long. Do you want to see it via a pager?'):
                    click.echo_via_pager('\n'.join(str(dso) for dso in object_list))
                    return
            for dso in object_list:
                click.echo(str(dso))
    except Exception as e:
        click.echo(click.style('ERROR: ', fg='red', bold=True) + str(e))


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument('ra')
@click.argument('dec')
@click.option('--radius', default=60, show_default=True,
              help='Maximum separation from starting coordinates (arcmin)')
@click.option('--catalog', type=click.Choice(['all', 'NGC', 'IC']),
              default='all', show_default=True,
              help='Search only for NGC or IC objects')
def nearby(ra, dec, radius, catalog):
    """List objects in proximity of given J2000 coordinates.

    Coordinates must be expressed in the form 'HH:MM:SS(.SS) +/-DD:MM:SS(.S)'
    """
    try:
        coords = '{} {}'.format(ra, dec)
        object_list = ongc.nearby(coords, radius, catalog)
        if len(object_list) == 0:
            click.secho('\nNo objects found within search radius!', bold=True)
            return
        if len(object_list) > 20:
            if click.confirm(click.style('WARNING: ', fg='yellow', bold=True)
                             + 'the result list is long. Do you want to see it via a pager?'):
                click.echo_via_pager('\n'.join('{:.2f}° --> {}'.format(dso[1], dso[0])
                                               for dso in object_list))
                return

        click.echo(click.style('\nObjects in proximity of ', bold=True)
                   + click.style(coords, fg='cyan')
                   + click.style(' from nearest to farthest:', bold=True))
        for dso in object_list:
            click.echo('{:.2f}° --> {}'.format(dso[1], dso[0]))
        if catalog != 'all':
            search_filter = ' and showing ' + catalog + ' objects only'
        else:
            search_filter = ''
        click.secho('(using a search radius of {} arcmin{})\n'.format(radius, search_filter),
                    fg='cyan')
    except Exception as e:
        click.echo(click.style('ERROR: ', fg='red', bold=True) + str(e))


@cli.command()
@click.argument('name')
def translate(name):
    """Search objects with alternative identifiers and return NGC or IC designation."""
    try:
        click.secho(str(ongc.searchAltId(name)), bold=True)
    except Exception as e:
        click.echo(click.style('ERROR: ', fg='red', bold=True) + str(e))


if __name__ == '__main__':
    cli()
