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

from os import environ
import click
import re

from pyongc import __version__ as version, ongc

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
            click.secho(f'{ongc.Dso(name)}', bold=True)
    except Exception as e:
        click.echo(f'{click.style("ERROR:", fg="red", bold=True)} {e}')


@cli.command()
def stats():
    """Show database statistics."""
    try:
        informations = ongc.stats()
        click.echo(f'\n{click.style("PyONGC version:", bold=True)} {version}')
        click.echo(f'{click.style("Database version:", bold=True)} {informations[1]}')
        click.echo(f'{click.style("Total number of objects in database:", bold=True)} '
                   f'{informations[2]}')
        click.secho('Object types statistics:', bold=True)
        for objType, objCount in informations[3]:
            click.echo(f'\t{objType:29}-> {objCount}')
    except Exception as e:
        click.echo(f'{click.style("ERROR:", fg="red", bold=True)} {e}')


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
                click.echo_via_pager('\n'.join(f'{dso[1]:.2f}° --> {dso[0]}'
                                               for dso in object_list))
                return

        click.secho(f'\n{start_obj.name} neighbors from nearest to farthest:', bold=True)
        for dso in object_list:
            click.echo(f'{dso[1]:.2f}° --> {dso[0]}')
        if catalog != 'all':
            search_filter = f' and showing {catalog} objects only'
        else:
            search_filter = ''
        click.secho(f'(using a search radius of {radius} arcmin{search_filter})\n', fg='cyan')
    except Exception as e:
        click.echo(f'{click.style("ERROR:", fg="red", bold=True)} {e}')


@cli.command()
@click.argument('obj1')
@click.argument('obj2')
def separation(obj1, obj2):
    """Return the apparent angular separation between two objects."""
    try:
        first = ongc.Dso(obj1)
        second = ongc.Dso(obj2)
        click.echo('Apparent angular separation between '
                   + click.style(first.name, fg='cyan')
                   + ' and '
                   + click.style(second.name, fg='cyan')
                   + ' is:')
        click.secho(ongc.getSeparation(obj1, obj2, style="text"), bold=True)
    except Exception as e:
        click.echo(f'{click.style("ERROR:", fg="red", bold=True)} {e}')


@cli.command()
@click.option('--catalog', type=click.Choice(['NGC', 'IC', 'M']),
              help='List only objects from specific catalog')
@click.option('--type',
              help=('List only objects of specific types. Accept multiple comma separated values. '
                    'See OpenNGC types list.'))
@click.option('--constellation',
              help=('List only objects in specific constellations. '
                    'Accept multiple comma separated values.'))
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
@click.option('--minra', help='List only objects with min R.A. HH:MM:SS[.ss]')
@click.option('--maxra', help='List only objects with max R.A. HH:MM:SS[.ss]')
@click.option('--mindec',
              help='List only objects above specified Declination +/-DD:MM:SS[.ss]')
@click.option('--maxdec',
              help='List only objects below specified Declination +/-DD:MM:SS[.ss]')
@click.option('--named', '-n', 'cname', help='List only objects with a common name like the input')
@click.option('--withname', '-N', is_flag=True, help='List only objects with common name')
@click.option('--out_file', '-O', type=click.File('w'),
              help='Output results to text file')
@click.option('--include_fields', '-I', help='Parameters for custom file output')
def search(out_file, include_fields, **kwargs):
    """Search in the database for objects with given parameters."""
    try:
        for r in ['minra', 'maxra']:
            if kwargs[r] is not None:
                pattern = re.compile(r'^(?:(\d{1,2}):(\d{1,2}):(\d{1,2}(?:\.\d{1,2})?))$')
                result = pattern.match(kwargs[r])
                hms = [float(x) for x in result.groups()[0:3]]
                kwargs[r] = hms[0] * 15 + hms[1] * 1/4 + hms[2] * 1/240
        for d in ['mindec', 'maxdec']:
            if kwargs[d] is not None:
                pattern = re.compile(r'^(?:([+-]?\d{1,2}):(\d{1,2}):(\d{1,2}(?:\.\d{1,2})?))$')
                result = pattern.match(kwargs[d])
                dms = [float(x) for x in result.groups()[0:3]]
                if dms[0] < 0:
                    kwargs[d] = dms[0] + dms[1] * -1/60 + dms[2] * -1/3600
                else:
                    kwargs[d] = dms[0] + dms[1] * 1/60 + dms[2] * 1/3600

        for v in ['type', 'constellation']:
            if kwargs[v] is not None:
                kwargs[v] = [x.strip() for x in kwargs[v].split(',')]

        object_list = ongc.listObjects(
            **{k: v for k, v in kwargs.items() if (v is not None and v is not False)})
        if len(object_list) == 0:
            click.secho('\nNo objects found with such parameters!', bold=True)
            return
        if out_file is not None:
            if include_fields is not None:
                include_fields = [x.strip() for x in include_fields.split(',')]
                if 'name' not in include_fields:
                    include_fields.insert(0, "name")
                lines = []
                lines.append(";".join(include_fields))
                for dso in object_list:
                    line = []
                    for param in include_fields:
                        column = str(getattr(dso, f'_{param}'))
                        line.append(column)
                    lines.append(";".join(line))
                out_file.write('\n'.join(lines))
                out_file.flush()
            else:
                out_file.write('\n'.join(dso._name for dso in object_list))
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
        click.echo(f'{click.style("ERROR:", fg="red", bold=True)} {e}')


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
                click.echo_via_pager('\n'.join(f'{dso[1]:.2f}° --> {dso[0]}'
                                               for dso in object_list))
                return

        click.echo(click.style('\nObjects in proximity of ', bold=True)
                   + click.style(coords, fg='cyan')
                   + click.style(' from nearest to farthest:', bold=True))
        for dso in object_list:
            click.echo(f'{dso[1]:.2f}° --> {dso[0]}')
        if catalog != 'all':
            search_filter = f' and showing {catalog} objects only'
        else:
            search_filter = ''
        click.secho(f'(using a search radius of {radius} arcmin{search_filter})\n', fg='cyan')
    except Exception as e:
        click.echo(f'{click.style("ERROR:", fg="red", bold=True)} {e}')


if __name__ == '__main__':
    cli()
