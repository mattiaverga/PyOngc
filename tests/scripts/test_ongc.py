# -*- coding:utf-8 -*-
#
# MIT License
#
# Copyright (c) 2018 Mattia Verga <mattia.verga@tiscali.it>
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

import click
from click.testing import CliRunner

from pyongc.scripts import ongc
from pyongc.ongc import __version__ as version

def test_view():
    runner = CliRunner()
    result = runner.invoke(ongc.view, ['ngc1'])
    assert result.exit_code == 0
    assert result.output == 'NGC0001, Galaxy in Peg\n'

def test_view_not_found():
    runner = CliRunner()
    result = runner.invoke(ongc.view, ['ngc1a'])
    assert result.exit_code == 0
    assert result.output == 'Object named NGC0001A not found in the database.\n'

def test_view_bad_name():
    runner = CliRunner()
    result = runner.invoke(ongc.view, ['bad'])
    assert result.exit_code == 0
    assert result.output == 'Wrong object name. Please insert a valid NGC or IC object name.\n'

def test_stats():
    runner = CliRunner()
    result = runner.invoke(ongc.stats)
    assert result.exit_code == 0
    assert 'PyONGC version: ' + version in result.output
