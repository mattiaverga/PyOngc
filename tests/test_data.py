# SPDX-FileCopyrightText: 2017 Mattia Verga <mattia.verga@tiscali.it>
#
# SPDX-License-Identifier: MIT

from unittest import mock
import pandas as pd
import pytest

from pyongc import data


class TestDataFrames():
    """Test DataFrames are returned as expected."""

    @mock.patch('pyongc.data.DBPATH', 'badpath')
    def test_fail_database_connection(self):
        """Test a failed connection to database."""
        with pytest.raises(OSError) as excinfo:
            data.all()
        assert 'There was a problem accessing database file' in str(excinfo.value)

    def test_all(self):
        """Test all() method."""
        objs = data.all()
        assert type(objs) is pd.core.frame.DataFrame
        assert objs[objs['type'] == 'Dup'].shape == (652, 33)

    def test_clusters_none(self):
        """Calling clusters with all parameters set to False should return None."""
        assert data.clusters(globular=False, open=False) is None

    @pytest.mark.parametrize('extra_ids', [True, False])
    def test_clusters_default(self, extra_ids):
        """Calling clusters with defaults should return GCl+OCl."""
        objs = data.clusters(extra_ids=extra_ids)
        assert objs[objs['type'] == 'GCl']['name'].size > 0
        assert objs[objs['type'] == 'OCl']['name'].size > 0
        assert objs[objs['type'] == '*Ass']['name'].size == 0
        if extra_ids:
            assert 'identifiers' in objs.columns.values.tolist()
        else:
            assert 'identifiers' not in objs.columns.values.tolist()

    def test_clusters_gcl_only(self):
        """Calling clusters without open should return GCl."""
        objs = data.clusters(open=False)
        assert objs[objs['type'] == 'GCl']['name'].size > 0
        assert objs[objs['type'] == 'OCl']['name'].size == 0
        assert objs[objs['type'] == '*Ass']['name'].size == 0

    def test_clusters_ocl_only(self):
        """Calling clusters without globular should return OCl."""
        objs = data.clusters(globular=False)
        assert objs[objs['type'] == 'GCl']['name'].size == 0
        assert objs[objs['type'] == 'OCl']['name'].size > 0
        assert objs[objs['type'] == '*Ass']['name'].size == 0

    def test_clusters_all(self):
        """Calling clusters with other should return GCl+OCl+*Ass+Cl+N."""
        objs = data.clusters(other=True)
        assert objs[objs['type'] == 'GCl']['name'].size > 0
        assert objs[objs['type'] == 'OCl']['name'].size > 0
        assert objs[objs['type'] == '*Ass']['name'].size > 0
        assert objs[objs['type'] == 'Cl+N']['name'].size > 0

    @pytest.mark.parametrize('extra_ids', [True, False])
    def test_galaxies(self, extra_ids):
        """Test calling galaxies()."""
        objs = data.galaxies(extra_ids=extra_ids)
        assert 'hubble' in objs.columns.values.tolist()
        if extra_ids:
            assert 'identifiers' in objs.columns.values.tolist()
        else:
            assert 'identifiers' not in objs.columns.values.tolist()

    @pytest.mark.parametrize('extra_ids', [True, False])
    def test_nebulae(self, extra_ids):
        """Test calling nebulae()."""
        objs = data.nebulae(extra_ids=extra_ids)
        assert 'cstarnames' in objs.columns.values.tolist()
        if extra_ids:
            assert 'identifiers' in objs.columns.values.tolist()
        else:
            assert 'identifiers' not in objs.columns.values.tolist()
