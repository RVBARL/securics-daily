#!/usr/bin/env python
# Copyright (C) 2023-2024, RV Bionics Group SpA.
# Created by Securics, Inc. <info@rvbionics.com>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

from unittest.mock import patch

import pytest

from securics.tests.util import InitWDBSocketMock

with patch('securics.core.common.securics_uid'):
    with patch('securics.core.common.securics_gid'):
        from securics.core.mitre import *


@patch('securics.core.utils.SecuricsDBConnection', return_value=InitWDBSocketMock(sql_schema_file='schema_mitre_test.sql'))
def test_SecuricsDBQueryMitreMetadata(mock_wdb):
    """Verify that the method connects correctly to the database and returns the correct type."""
    db_query = SecuricsDBQueryMitreMetadata()
    data = db_query.run()

    assert isinstance(db_query, SecuricsDBQueryMitre) and isinstance(data, dict)


@pytest.mark.parametrize('wdb_query_class', [
    SecuricsDBQueryMitreGroups,
    SecuricsDBQueryMitreMitigations,
    SecuricsDBQueryMitreReferences,
    SecuricsDBQueryMitreTactics,
    SecuricsDBQueryMitreTechniques,
    SecuricsDBQueryMitreSoftware

])
@patch('securics.core.utils.SecuricsDBConnection', return_value=InitWDBSocketMock(sql_schema_file='schema_mitre_test.sql'))
def test_SecuricsDBQueryMitre_classes(mock_wdb, wdb_query_class):
    """Verify that the method connects correctly to the database and returns the correct types."""
    db_query = wdb_query_class()
    data = db_query.run()

    assert isinstance(db_query, SecuricsDBQueryMitre) and isinstance(data, dict)

    # All items have all the related_items (relation_fields) and their type is list
    try:
        assert all(
            isinstance(data_item[related_item], list) for related_item in db_query.relation_fields for data_item in
            data['items'])
    except KeyError:
        pytest.fail("Related item not found in data obtained from query")


@pytest.mark.parametrize('mitre_wdb_query_class', [
    SecuricsDBQueryMitreGroups,
    SecuricsDBQueryMitreMitigations,
    SecuricsDBQueryMitreReferences,
    SecuricsDBQueryMitreTactics,
    SecuricsDBQueryMitreTechniques,
    SecuricsDBQueryMitreSoftware
])
@patch('securics.core.utils.SecuricsDBConnection')
def test_get_mitre_items(mock_wdb, mitre_wdb_query_class):
    """Test get_mitre_items function."""
    info, data = get_mitre_items(mitre_wdb_query_class)

    db_query_to_compare = mitre_wdb_query_class()

    assert isinstance(info['allowed_fields'], set) and info['allowed_fields'] == set(
        db_query_to_compare.fields.keys()).union(
        db_query_to_compare.relation_fields).union(db_query_to_compare.extra_fields)
    assert isinstance(info['min_select_fields'], set) and info[
        'min_select_fields'] == db_query_to_compare.min_select_fields
