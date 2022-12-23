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

from click.testing import CliRunner
import os.path
import mock

from pyongc.scripts import ongc
from pyongc import __version__ as version


def test_view():
    runner = CliRunner()
    result = runner.invoke(ongc.view, ['ngc1'])
    assert result.exit_code == 0
    assert result.output == 'NGC0001, Galaxy in Peg\n'


def test_view_details():
    runner = CliRunner()
    result = runner.invoke(ongc.view, ['ngc1', '--details'])
    assert result.exit_code == 0
    assert result.output == (
        "+-----------------------------------------------------------------------------+\n"
        "| Id: 5596      Name: NGC0001           Type: Galaxy                          |\n"
        "| R.A.: 00:07:15.84      Dec.: +27:42:29.1      Constellation: Peg            |\n"
        "+-----------------------------------------------------------------------------+\n"
        "| Major axis: 1.57'      Minor axis: 1.07'      Position angle: 112°          |\n"
        "| B-mag: 13.69   V-mag: 12.93   J-mag: 10.78   H-mag: 10.02   K-mag: 9.76     |\n"
        "|                                                                             |\n"
        "| Parallax: N/A          Radial velocity: 4536km/s      Redshift: 0.015245    |\n"
        "|                                                                             |\n"
        "| Proper apparent motion in RA: N/A                                           |\n"
        "| Proper apparent motion in Dec: N/A                                          |\n"
        "|                                                                             |\n"
        "| Surface brightness: 23.13     Hubble classification: Sb                     |\n"
        "+-----------------------------------------------------------------------------+\n"
        "| Other identifiers:                                                          |\n"
        "|    2MASX J00071582+2742291, IRAS 00047+2725, MCG +04-01-025, PGC 000564,    |\n"
        "|    UGC 00057                                                                |\n"
        "+-----------------------------------------------------------------------------+\n\n")


def test_view_not_found():
    runner = CliRunner()
    result = runner.invoke(ongc.view, ['ngc1a'])
    assert result.exit_code == 0
    assert result.output == 'ERROR: Object named NGC0001A not found in the database.\n'


def test_view_bad_name():
    runner = CliRunner()
    result = runner.invoke(ongc.view, ['bad'])
    assert result.exit_code == 0
    assert result.output == ('ERROR: The name "BAD" is not recognized.\n')


def test_stats():
    runner = CliRunner()
    result = runner.invoke(ongc.stats)
    assert result.exit_code == 0
    assert 'PyONGC version: ' + version in result.output


@mock.patch('pyongc.ongc.DBPATH', 'badpath')
def test_stats_database_error():
    runner = CliRunner()
    result = runner.invoke(ongc.stats)
    assert result.exit_code == 0
    assert 'ERROR: There was a problem accessing database file at badpath\n' in result.output


def test_neighbors():
    runner = CliRunner()
    result = runner.invoke(ongc.neighbors, ['ngc1'])
    assert result.exit_code == 0
    assert result.output == (
        '\nNGC0001 neighbors from nearest to farthest:\n'
        '0.03° --> NGC0002, Galaxy in Peg\n'
        '0.09° --> NGC7839, Double star in Peg\n'
        '0.18° --> NGC7833, Object of other/unknown type in Peg\n'
        '0.26° --> IC0001, Double star in Peg\n'
        '0.40° --> NGC0016, Galaxy in Peg\n'
        '0.47° --> NGC0018, Double star in Peg\n'
        '(using a search radius of 30 arcmin)\n\n')


def test_neighbors_with_catalog_filter():
    runner = CliRunner()
    result = runner.invoke(ongc.neighbors, ['ngc1', '--catalog=IC'])
    assert result.exit_code == 0
    assert result.output == (
        '\nNGC0001 neighbors from nearest to farthest:\n'
        '0.26° --> IC0001, Double star in Peg\n'
        '(using a search radius of 30 arcmin and showing IC objects only)\n\n')


def test_neighbors_with_radius_filter():
    runner = CliRunner()
    result = runner.invoke(ongc.neighbors, ['ngc1', '--radius=12'])
    assert result.exit_code == 0
    assert result.output == (
        '\nNGC0001 neighbors from nearest to farthest:\n'
        '0.03° --> NGC0002, Galaxy in Peg\n'
        '0.09° --> NGC7839, Double star in Peg\n'
        '0.18° --> NGC7833, Object of other/unknown type in Peg\n'
        '(using a search radius of 12 arcmin)\n\n')


def test_neighbors_no_results():
    runner = CliRunner()
    result = runner.invoke(ongc.neighbors, ['ngc1', '--radius=1'])
    assert result.exit_code == 0
    assert result.output == '\nNo objects found within search radius!\n'


def test_neighbors_bad_name():
    runner = CliRunner()
    result = runner.invoke(ongc.neighbors, ['bad'])
    assert result.exit_code == 0
    assert result.output == ('ERROR: The name "BAD" is not recognized.\n')


def test_neighbors_with_pager():
    runner = CliRunner()
    result = runner.invoke(ongc.neighbors, ['ngc1', '--radius=600'], input='y')
    assert result.exit_code == 0
    assert 'WARNING: the result list is long. Do you want to see it via a pager?' in result.output
    assert '\nNGC0001 neighbors from nearest to farthest:\n' not in result.output


def test_separation():
    runner = CliRunner()
    result = runner.invoke(ongc.separation, ['ngc1', 'ngc2'])
    assert result.exit_code == 0
    assert result.output == ('Apparent angular separation between NGC0001 and NGC0002 is:\n'
                             '0° 1m 48.32s\n')


def test_separation_bad_name():
    runner = CliRunner()
    result = runner.invoke(ongc.separation, ['ngc1', 'bad'])
    assert result.exit_code == 0
    assert result.output == ('ERROR: The name "BAD" is not recognized.\n')


def test_search():
    runner = CliRunner()
    result = runner.invoke(ongc.search)
    assert result.exit_code == 0
    assert 'WARNING: the result list is long. Do you want to see it via a pager?' in result.output
    assert result.output.endswith('UGC05470, Galaxy in Leo\n')


def test_search_with_catalog_filter():
    runner = CliRunner()
    result = runner.invoke(ongc.search, ['--catalog=M'])
    assert result.exit_code == 0
    assert 'WARNING: the result list is long. Do you want to see it via a pager?' in result.output
    assert result.output.endswith('NGC0205, Galaxy in And\n')


def test_search_with_type_filter():
    runner = CliRunner()
    result = runner.invoke(ongc.search, ['--type=*'])
    assert result.exit_code == 0
    assert 'WARNING: the result list is long. Do you want to see it via a pager?' in result.output
    assert result.output.endswith('NGC7830, Star in Psc\n')


def test_search_with_multiple_types_filter():
    runner = CliRunner()
    result = runner.invoke(ongc.search, ['--type=*,**'])
    assert result.exit_code == 0
    assert 'WARNING: the result list is long. Do you want to see it via a pager?' in result.output
    assert result.output.endswith('M040, Double star in UMa\n')


def test_search_with_constellation_filter():
    runner = CliRunner()
    result = runner.invoke(ongc.search, ['--constellation=aql'])
    assert result.exit_code == 0
    assert 'WARNING: the result list is long. Do you want to see it via a pager?' in result.output
    assert result.output.endswith('NGC6941, Galaxy in Aql\n')


def test_search_with_multiple_constellations_filter():
    runner = CliRunner()
    result = runner.invoke(ongc.search, ['--constellation=aql,cyg'])
    assert result.exit_code == 0
    assert 'WARNING: the result list is long. Do you want to see it via a pager?' in result.output
    assert result.output.endswith('NGC7175, Open Cluster in Cyg\n')


def test_search_with_minsize_filter():
    runner = CliRunner()
    result = runner.invoke(ongc.search, ['--minsize=5'])
    assert result.exit_code == 0
    assert 'WARNING: the result list is long. Do you want to see it via a pager?' in result.output
    assert result.output.endswith('UGC05470, Galaxy in Leo\n')


def test_search_with_maxsize_filter():
    runner = CliRunner()
    result = runner.invoke(ongc.search, ['--maxsize=0.5'])
    assert result.exit_code == 0
    assert 'WARNING: the result list is long. Do you want to see it via a pager?' in result.output
    assert result.output.endswith('NGC5457, Galaxy in UMa\n')


def test_search_with_uptobmag_filter():
    runner = CliRunner()
    result = runner.invoke(ongc.search, ['--uptobmag=8'])
    assert result.exit_code == 0
    assert 'WARNING: the result list is long. Do you want to see it via a pager?' in result.output
    assert result.output.endswith('Mel071, Open Cluster in Pup\n')


def test_search_with_uptovmag_filter():
    runner = CliRunner()
    result = runner.invoke(ongc.search, ['--uptovmag=6'])
    assert result.exit_code == 0
    assert 'WARNING: the result list is long. Do you want to see it via a pager?' in result.output
    assert result.output.endswith('Mel022, Open Cluster in Tau\n')


def test_search_with_minra_filter():
    runner = CliRunner()
    result = runner.invoke(ongc.search, ['--minra=23:52:00.00'])
    assert result.exit_code == 0
    assert 'WARNING: the result list is long. Do you want to see it via a pager?' in result.output
    assert result.output.endswith('H21, Open Cluster in Cas\n')


def test_search_with_maxra_filter():
    runner = CliRunner()
    result = runner.invoke(ongc.search, ['--maxra=0:8:0'])
    assert result.exit_code == 0
    assert 'WARNING: the result list is long. Do you want to see it via a pager?' in result.output
    assert result.output.endswith('NGC7840, Galaxy in Psc\n')


def test_search_with_minra_maxra_filter():
    runner = CliRunner()
    result = runner.invoke(ongc.search, ['--minra=23:56:0', '--maxra=0:4:0'])
    assert result.exit_code == 0
    assert 'WARNING: the result list is long. Do you want to see it via a pager?' in result.output
    assert result.output.endswith('NGC7822, HII Ionized region in Cep\n')


def test_search_with_mindec_filter():
    runner = CliRunner()
    result = runner.invoke(ongc.search, ['--mindec=85:00:00.00'])
    assert result.exit_code == 0
    assert result.output.endswith('NGC3172, Galaxy in UMi\n')


def test_search_with_maxdec_filter():
    runner = CliRunner()
    result = runner.invoke(ongc.search, ['--maxdec=-85:0:0'])
    assert result.exit_code == 0
    assert result.output.endswith('NGC6438A, Galaxy in Oct\n')


def test_search_with_mindec_maxdec_filter():
    runner = CliRunner()
    result = runner.invoke(ongc.search, ['--mindec=-1:00:00', '--maxdec=+1:0:0'])
    assert result.exit_code == 0
    assert 'WARNING: the result list is long. Do you want to see it via a pager?' in result.output
    assert result.output.endswith('NGC7787, Galaxy in Psc\n')


def test_search_by_common_name():
    runner = CliRunner()
    result = runner.invoke(ongc.search, ['--named=california'])
    assert result.exit_code == 0
    assert result.output == 'NGC1499, Nebula in Per\n'


def test_search_with_common_name():
    runner = CliRunner()
    result = runner.invoke(ongc.search, ['--constellation=aql', '-N'])
    assert result.exit_code == 0
    assert result.output == 'NGC6741, Planetary Nebula in Aql\n'


def test_search_to_file():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(ongc.search, ['--constellation=aql', '--out_file=test.txt'])
        assert result.exit_code == 0
        assert os.path.isfile('test.txt')
        with open('test.txt') as f:
            assert '\nNGC6915\n' in f.read()


def test_search_to_custom_file():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(ongc.search, [
            '--include_fields=name,type,cstarnames',
            '--constellation=her',
            '--out_file=test.csv',
        ])
        assert result.exit_code == 0
        assert os.path.isfile('test.csv')
        with open('test.csv') as f:
            assert '\nIC4593;Planetary Nebula;BD +12 2966,HD 145649\n' in f.read()


def test_search_to_custom_file_invalid_field():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(ongc.search, [
            '--constellation=her',
            '--out_file=test.csv',
            '--include_fields=test'
        ])
        assert result.exit_code == 0
        assert result.output == "ERROR: 'Dso' object has no attribute '_test'\n"
        assert not os.path.isfile('test.csv')


def test_search_no_results():
    runner = CliRunner()
    result = runner.invoke(ongc.search, ['--type=*', '--minsize=5'])
    assert result.exit_code == 0
    assert result.output == '\nNo objects found with such parameters!\n'


def test_search_with_pager():
    runner = CliRunner()
    result = runner.invoke(ongc.search, ['--catalog=M'], input='y')
    assert result.exit_code == 0
    assert 'WARNING: the result list is long. Do you want to see it via a pager?' in result.output
    assert result.output.endswith('NGC0205, Galaxy in And\n')


@mock.patch('pyongc.ongc.DBPATH', 'badpath')
def test_search_database_error():
    runner = CliRunner()
    result = runner.invoke(ongc.search)
    assert result.exit_code == 0
    assert 'ERROR: There was a problem accessing database file at badpath\n' in result.output


def test_nearby():
    runner = CliRunner()
    result = runner.invoke(ongc.nearby, ['11:08:44', '-00:09:01.3'])
    assert result.exit_code == 0
    assert result.output == (
        '\nObjects in proximity of 11:08:44 -00:09:01.3 '
        'from nearest to farthest:\n'
        '0.18° --> IC0673, Galaxy in Leo\n'
        '0.74° --> NGC3521, Galaxy in Leo\n'
        '0.98° --> IC0671, Galaxy in Leo\n'
        '(using a search radius of 60 arcmin)\n\n')


def test_nearby_with_catalog_filter():
    runner = CliRunner()
    result = runner.invoke(ongc.nearby, ['11:08:44', '-00:09:01.3', '--catalog=IC'])
    assert result.exit_code == 0
    assert result.output == (
        '\nObjects in proximity of 11:08:44 -00:09:01.3 '
        'from nearest to farthest:\n'
        '0.18° --> IC0673, Galaxy in Leo\n'
        '0.98° --> IC0671, Galaxy in Leo\n'
        '(using a search radius of 60 arcmin and showing IC objects only)\n\n')


def test_nearby_with_radius_filter():
    runner = CliRunner()
    result = runner.invoke(ongc.nearby, ['11:08:44', '+00:09:01.3', '--radius=30'])
    assert result.exit_code == 0
    assert result.output == (
        '\nObjects in proximity of 11:08:44 +00:09:01.3 '
        'from nearest to farthest:\n'
        '0.30° --> IC0673, Galaxy in Leo\n'
        '(using a search radius of 30 arcmin)\n\n')


def test_nearby_no_results():
    runner = CliRunner()
    result = runner.invoke(ongc.nearby, ['11:08:44', '-00:09:01.3', '--radius=1'])
    assert result.exit_code == 0
    assert result.output == '\nNo objects found within search radius!\n'


def test_nearby_bad_name():
    runner = CliRunner()
    result = runner.invoke(ongc.nearby, ['11:08:44', '00:09:01.3'])
    assert result.exit_code == 0
    assert result.output == ('ERROR: This text cannot be recognized as coordinates: '
                             '11:08:44 00:09:01.3\n')


def test_nearby_with_pager():
    runner = CliRunner()
    result = runner.invoke(ongc.nearby, ['11:08:44', '-00:09:01.3', '--radius=600'], input='y')
    assert result.exit_code == 0
    assert 'WARNING: the result list is long. Do you want to see it via a pager?' in result.output
    assert '\nObjects in proximity of 11:08:44 -00:09:01.3' not in result.output
