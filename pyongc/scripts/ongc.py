#!/usr/bin/python3
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

"""A command line browser for OpenNGC database.

    Usage: ongc [OPTIONS] COMMAND [ARGS]...
"""

from pyongc import ongc
import click


@click.group()
def cli():
    pass


@cli.command(help='Prints out object information')
@click.argument('name')
@click.option('--details/--no-details', default=False,
              help='Shows detailed information or just summary')
def view(name, details):
    try:
        if details:
            click.echo(ongc.printDetails(ongc.Dso(name)))
        else:
            click.echo(ongc.Dso(name))
    except Exception as e:
        click.echo(e)


@cli.command(help='Shows database statistics')
def stats():
    try:
        informations = ongc.stats()
        click.echo('PyONGC version: ' + ongc.__version__)
        click.echo('Database version: ' + str(informations[1]))
        click.echo('Total number of objects in database: ' + str(informations[2]))
        click.echo('Object types statistics:')
        for objType, objCount in informations[3]:
            click.echo('{:29}'.format(objType) + '-> ' + str(objCount))
    except Exception as e:
        click.echo(e)


if __name__ == '__main__':
    cli()
