#!/usr/bin/env python
# Copyright (C) 2023-2024, RV Bionics Group SpA.
# Created by Securics, Inc. <info@rvbionics.com>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

import os
import sys
import glob
from unittest.mock import patch, MagicMock
import pytest
from securics.core.common import USER_DECODERS_PATH


with patch('securics.core.common.getgrnam'):
    with patch('securics.core.common.getpwnam'):
        sys.modules['securics.rbac.orm'] = MagicMock()
        import securics.rbac.decorators
        del sys.modules['securics.rbac.orm']
        from securics.tests.util import RBAC_bypasser
        securics.rbac.decorators.expose_resources = RBAC_bypasser

        from securics.core.exception import SecuricsInternalError, SecuricsError
        from securics.core.results import AffectedItemsSecuricsResult
        from securics import decoder


# Variables

test_data_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
decoder_ossec_conf = {
    'ruleset': {
        'decoder_dir': ['tests/data/decoders', 
                        'tests/data/etc/decoders',
                        'tests/data/etc/decoders2',
                        'tests/data/etc/decoders/subpath'],
        'decoder_exclude': 'test2_decoders.xml'
    }
}

decoder_ossec_conf_2 = {
    'ruleset': {
        'decoder_dir': ['tests/data/decoders'],
        'decoder_exclude': 'wrong_decoders.xml'
    }
}


# Module patches

@pytest.fixture(scope='module', autouse=True)
def mock_securics_paths():
    """Mock securics paths."""
    with patch('securics.core.common.SECURICS_PATH', new=test_data_path):
        with patch('securics.core.configuration.get_ossec_conf', return_value=decoder_ossec_conf):
            with patch('securics.core.common.DECODERS_PATH',
                       new=os.path.join(test_data_path, "tests", "data", "decoders")):
                with patch('securics.core.common.USER_DECODERS_PATH',
                           new=os.path.join(test_data_path, "tests", "data", "etc", "decoders")):
                    with patch('securics.decoder.to_relative_path',
                               side_effect=lambda x: os.path.relpath(x, securics.core.common.SECURICS_PATH)):
                        yield


# Tests

@pytest.mark.parametrize('names, status, filename, relative_dirname, parents, expected_names, expected_total_failed', [
    (None, None, None, None, False, {'agent-buffer', 'json', 'agent-upgrade', 'securics', 'agent-restart'}, 0),
    (['agent-buffer'], None, None, None, False, {'agent-buffer'}, 0),
    (['agent-buffer', 'non_existing'], None, None, None, False, {'agent-buffer'}, 1),
    (None, 'enabled', None, None, False, {'agent-buffer', 'agent-upgrade', 'securics', 'agent-restart'}, 0),
    (None, 'disabled', None, None, False, {'json'}, 0),
    (['agent-upgrade', 'non_existing', 'json'], 'enabled', None, None, False, {'agent-upgrade'}, 1),
    (None, None, 'test1_decoders.xml', None, False, {'agent-buffer', 'agent-upgrade', 'securics', 'agent-restart'}, 0),
    (None, None, 'test2_decoders.xml', 'tests/data/decoders', False, {'json'}, 0),
    (None, 'all', None, 'tests/data/decoders', True, {'securics', 'json'}, 0),
    (None, 'all', None, 'nothing_here', False, set(), 0)
])
def test_get_decoders(names, status, filename, relative_dirname, parents, expected_names, expected_total_failed):
    wrong_decoder_original_path = os.path.join(test_data_path, 'tests/data/decoders', 'wrong_decoders.xml')
    wrong_decoder_tmp_path = os.path.join(test_data_path, 'tests/data', 'wrong_decoders.xml')
    try:
        os.rename(wrong_decoder_original_path, wrong_decoder_tmp_path)
        # UUT call
        result = decoder.get_decoders(names=names, status=status, filename=filename, relative_dirname=relative_dirname,
                                      parents=parents)
        assert isinstance(result, AffectedItemsSecuricsResult)
        # Build result names set from response for filter validation
        result_names = {d['name'] for d in result.affected_items}
        assert result_names == expected_names
        # Assert failed items length matches expected result
        assert result.total_failed_items == expected_total_failed
    finally:
        os.rename(wrong_decoder_tmp_path, wrong_decoder_original_path)


@pytest.mark.parametrize('conf, exception', [
    (decoder_ossec_conf, None),
    ({'ruleset': None}, SecuricsInternalError(1500))
])
def test_get_decoders_files(conf, exception):
    """Test get_decoders_files function"""
    with patch('securics.core.configuration.get_ossec_conf', return_value=conf):
        try:
            # UUT call
            result = decoder.get_decoders_files()
            assert isinstance(result, AffectedItemsSecuricsResult)
            # Assert result is a list with at least one dict element with the appropriate fields
            assert isinstance(result.affected_items, list)
            assert len(result.affected_items) != 0
            for item in result.affected_items:
                assert {'filename', 'relative_dirname', 'status'}.issubset(set(item))
            assert result.total_affected_items == len(result.affected_items)
        except SecuricsInternalError as exc:
            # If the UUT call returns an exception we check it has the appropriate error code
            assert exc.code == exception.code


@pytest.mark.parametrize('status, relative_dirname, filename, expected_files', [
    (None, None, None, {'test1_decoders.xml', 'test2_decoders.xml', 'test3_decoders.xml', 'wrong_decoders.xml'}),
    ('all', None, None, {'test1_decoders.xml', 'test2_decoders.xml', 'test3_decoders.xml', 'wrong_decoders.xml'}),
    ('enabled', None, None, {'test1_decoders.xml', 'test3_decoders.xml', 'wrong_decoders.xml'}),
    ('disabled', None, None, {'test2_decoders.xml'}),
    ('all', 'tests/data/decoders', None, {'test1_decoders.xml', 'test2_decoders.xml', 'wrong_decoders.xml'}),
    ('all', 'wrong_path', None, set()),
    ('disabled', 'tests/data/decoders', None, {'test2_decoders.xml'}),
    (None, 'tests/data/decoders', 'test2_decoders.xml', {'test2_decoders.xml'}),
    ('disabled', 'tests/data/decoders', 'test2_decoders.xml', {'test2_decoders.xml'}),
    ('enabled', 'tests/data/decoders', 'test2_decoders.xml', set()),
    ('enabled', None, 'test1_decoders.xml', {'test1_decoders.xml'}),
    (None, None, ['test1_decoders.xml', 'test2_decoders.xml'], {'test1_decoders.xml', 'test2_decoders.xml'}),
    ('enabled', None, ['test1_decoders.xml', 'test2_decoders.xml'], {'test1_decoders.xml'}),
    ('disabled', None, ['wrong_decoders.xml', 'test2_decoders.xml', 'non_existing.xml'], {'test2_decoders.xml'}),
    (None, None, 'non_existing.xml', set()),
])
def test_get_decoders_files_filters(status, relative_dirname, filename, expected_files):
    # UUT call
    result = decoder.get_decoders_files(status=status, relative_dirname=relative_dirname, filename=filename)
    assert isinstance(result, AffectedItemsSecuricsResult)
    # Build result_files set from response for filter validation
    result_files = {d['filename'] for d in result.affected_items}
    assert result_files == expected_files


@pytest.mark.parametrize('filename, relative_dirname, result', [
    ('test1_decoders.xml', None, 'tests/data/decoders/test1_decoders.xml'),
    ('test3_decoders.xml', None, 'tests/data/etc/decoders/test3_decoders.xml'),
    ('test2_decoders.xml', 'tests/data/etc/decoders/subpath', 'tests/data/etc/decoders/subpath/test2_decoders.xml'),
    ('test3_decoders.xml', 'tests/data/etc/decoders/subpath', 'tests/data/etc/decoders/subpath/test3_decoders.xml'),
    ('test3_decoders.xml', 'tests/data/etc/decoders/subpath/', 'tests/data/etc/decoders/subpath/test3_decoders.xml'),
    ('not_found.xml', None, ''),
])
def test_get_decoder_file_path(filename, relative_dirname, result, mock_securics_paths):
    """Test get_decoder_file_path function."""
    res = decoder.get_decoder_file_path(filename=filename, 
                                         relative_dirname=relative_dirname)
    assert res == os.path.join(securics.core.common.SECURICS_PATH, result) if result else not res and isinstance(res, str)


@pytest.mark.parametrize('filename, raw, relative_dirname, contains', [
    ('test1_decoders.xml', True, None, None),
    ('test1_decoders.xml', False, None, None),
    ('test3_decoders.xml', True, None, 'DECODER IN USER_DECODERS_PATH.'),
    ('test2_decoders.xml', True, 'tests/data/etc/decoders/subpath', None),
    ('test3_decoders.xml', True, 'tests/data/etc/decoders/subpath',
     'DECODER IN USER_DECODERS_PATH/subpath'),
    ('test3_decoders.xml', True, 'tests/data/etc/decoders/subpath/',
     'DECODER IN USER_DECODERS_PATH/subpath'),
])
def test_get_decoder_file(filename, raw, relative_dirname, contains, mock_securics_paths):
    """Test get file function.

    Parameters
    ----------
    filename : str
        Decoder filename.
    raw: bool
        If raw is True, assert that the content is string.
        If raw is False, assert that a structure is returned.
    relative_dirname: str
        Relative path of the file.
    contains: str
        Assert that contains parameter is found in the file content. Only used when raw is True.
    """
    result = decoder.get_decoder_file(filename=filename, raw=raw, relative_dirname=relative_dirname)

    if raw:
        # Assert the result is a plain text str
        assert isinstance(result, str)
        if contains:
            assert result.find(contains)
    else:
        # Assert the result is an AffectedItemsSecuricsResult
        assert isinstance(result, AffectedItemsSecuricsResult)
        assert result.affected_items
        assert not result.failed_items


def test_get_decoder_file_exceptions():
    """Test exceptions on get method."""

    # File does not exist in default ruleset
    result = decoder.get_decoder_file(filename='non_existing_file.xml')
    assert not result.affected_items
    assert result.render()['data']['failed_items'][0]['error']['code'] == 1503

    # File does not exist in user ruleset
    result = decoder.get_decoder_file(filename='non_existing_file.xml',
                                      raw=False, relative_dirname=USER_DECODERS_PATH)
    assert not result.affected_items
    assert result.render()['data']['failed_items'][0]['error']['code'] == 1503

    # File exists in default ruleset but not in custom ruleset
    result = decoder.get_decoder_file(filename='test1_decoders.xml',
                                      raw=False, relative_dirname=USER_DECODERS_PATH)
    assert not result.affected_items
    assert result.render()['data']['failed_items'][0]['error']['code'] == 1503

    # Invalid XML
    result = decoder.get_decoder_file(filename='wrong_decoders.xml')
    assert not result.affected_items
    assert result.render()['data']['failed_items'][0]['error']['code'] == 1501

    # File permissions
    with patch('builtins.open', side_effect=PermissionError):
        result = decoder.get_decoder_file(filename='test2_decoders.xml')
        assert not result.affected_items
        assert result.render()['data']['failed_items'][0]['error']['code'] == 1502


@pytest.mark.parametrize('relative_dirname, res_path, err_code', [
    (None, 'tests/data/etc/decoders', None),
    ('tests/data/etc/decoders/', 'tests/data/etc/decoders', None),
    ('tests/data/etc/decoders/subpath', 'tests/data/etc/decoders/subpath', None),
    ('tests/data/etc/decoders/subpath/', 'tests/data/etc/decoders/subpath', None),
    ('tests/data/etc/decoders3', 'tests/data/etc/decoders3', 1505),
    ('tests/data/decoders', 'tests/data/decoders', 1506),
    ('tests/data/etc/decoders2', 'tests/data/etc/decoders2', 1507),
])
def test_validate_upload_delete_dir(relative_dirname, res_path, err_code):
    """Test validate_upload_delete_dir function."""
    ret_path, ret_err = decoder.validate_upload_delete_dir(relative_dirname = relative_dirname)
    assert ret_path == res_path and (ret_err.code == err_code if err_code else not ret_err)


@pytest.mark.parametrize('file, relative_dirname, overwrite, decoder_path', [
    ('test1_decoders.xml', None, True, "tests/data/etc/decoders/test1_decoders.xml"),
    ('test2_decoders.xml', 'tests/data/etc/decoders/subpath', True,
     'tests/data/etc/decoders/subpath/test2_decoders.xml'),
    ('test_new_decoders.xml', None, False,
     'tests/data/etc/decoders/test_new_decoders.xml'),
    ('test_new_decoders.xml', 'tests/data/etc/decoders/subpath/', False,
     'tests/data/etc/decoders/subpath/test_new_decoders.xml'),
])
@patch('securics.decoder.delete_decoder_file')
@patch('securics.decoder.full_copy')
@patch('securics.decoder.validate_securics_xml')
@patch('securics.decoder.upload_file')
@patch('securics.decoder.remove')
@patch('securics.decoder.safe_move')
@patch('securics.decoder.validate_dummy_logtest')
def test_upload_file(mock_logtest, mock_safe_move, mock_remove, mock_upload_file,
                     mock_xml, mock_full_copy, mock_delete, mock_securics_paths,
                     file, relative_dirname, overwrite, decoder_path):
    """Test uploading a decoder file.

    Parameters
    ----------
    file : str
        Decoder filename.
    relative_dirname: str
        Relative path of the file.
    overwrite : boolean
        True for updating existing files, False otherwise.
    decoder_path: str
        Relative path of the file.
    """

    content = 'test'
    ret_validation = decoder.validate_upload_delete_dir(relative_dirname=relative_dirname)
    with patch('securics.decoder.validate_upload_delete_dir', return_value=ret_validation):
        with patch('securics.decoder.exists', return_value=overwrite):
            with patch('securics.decoder.to_relative_path',
                    side_effect=lambda x: os.path.relpath(x, securics.core.common.SECURICS_PATH)):
                result = decoder.upload_decoder_file(filename=file, content=content,
                                                        relative_dirname=relative_dirname,
                                                        overwrite=overwrite)

            # Assert data match what was expected, type of the result 
            # and correct parameters in delete() method.
            assert isinstance(result, AffectedItemsSecuricsResult), 'No expected result type'

            mock_xml.assert_called_once_with(content)
            mock_upload_file.assert_called_once_with(content, decoder_path)
            if overwrite:
                full_path = os.path.join(rvbionics.common.SECURICS_PATH, decoder_path)
                backup_file = full_path+'.backup'
                mock_full_copy.assert_called_once_with(full_path, backup_file), \
                'full_copy function not called with expected parameters'
                mock_delete.assert_called_once_with(filename=file,
                                                    relative_dirname=os.path.dirname(decoder_path)), \
                'delete_decoder_file function not called with expected parameters'
                mock_remove.assert_called_once()
                mock_safe_move.assert_called_once()


@patch('securics.decoder.delete_decoder_file', side_effect=SecuricsError(1019))
@patch('securics.decoder.upload_file')
@patch('securics.decoder.safe_move')
@patch('securics.core.utils.check_remote_commands')
def test_upload_file_ko(*_):
    """Test exceptions on upload function."""
    ret_validation = decoder.validate_upload_delete_dir(relative_dirname=None)
    with patch('securics.decoder.validate_upload_delete_dir', return_value=ret_validation):
        with patch('securics.decoder.exists'):
            # Error when file exists and overwrite is not True
            result = decoder.upload_decoder_file(filename='test_decoders.xml',
                                                content='test', overwrite=False)
            assert isinstance(result, AffectedItemsSecuricsResult), 'No expected result type'
            assert result.render()['data']['failed_items'][0]['error']['code'] == 1905,\
            'Error code not expected.'

    # Error when content is empty
    result = decoder.upload_decoder_file(filename='no_exist.xml', content='', overwrite=False)
    assert isinstance(result, AffectedItemsSecuricsResult), 'No expected result type'
    assert result.render()['data']['failed_items'][0]['error']['code'] == 1112,\
        'Error code not expected.'

    # Error doing backup
    result = decoder.upload_decoder_file(filename='test3_decoders.xml',
                                         content='test', overwrite=True)
    assert isinstance(result, AffectedItemsSecuricsResult), 'No expected result type'
    assert result.render()['data']['failed_items'][0]['error']['code'] == 1019,\
        'Error code not expected.'

    # Error relative_path is not declared in decoder_dir
    result = decoder.upload_decoder_file(filename='test3_decoders.xml',
                                        relative_dirname='tests/data/etc/decoders3',
                                        content='test')
    assert isinstance(result, AffectedItemsSecuricsResult), 'No expected result type'
    assert result.render()['data']['failed_items'][0]['error']['code'] == 1505,\
        'Error code not expected.'

    # Error uploading decoder to default ruleset
    result = decoder.upload_decoder_file(filename='test3_decoders.xml',
                                         relative_dirname='tests/data/decoders',
                                         content='test', overwrite=True)
    assert isinstance(result, AffectedItemsSecuricsResult), 'No expected result type'
    assert result.render()['data']['failed_items'][0]['error']['code'] == 1506,\
        'Error code not expected.'

    # Error upload file to existing decoder_dir but the directory is not found
    result = decoder.upload_decoder_file(filename='test3_decoders.xml',
                                        relative_dirname='tests/data/etc/decoders2',
                                        content='test')
    assert isinstance(result, AffectedItemsSecuricsResult), 'No expected result type'
    assert result.render()['data']['failed_items'][0]['error']['code'] == 1507,\
        'Error code not expected.'
    
    # clean backup files
    search_pattern = os.path.join(securics.core.common.SECURICS_PATH, "**", "*.backup")
    for bkp in glob.glob(search_pattern, recursive=True):
        os.remove(bkp)


@pytest.mark.parametrize('filename, relative_dirname', [
    ('test1_decoders.xml', None),
    ('test3_decoders.xml', None),
    ('test2_decoders.xml', 'tests/data/etc/decoders/subpath'),
    ('test3_decoders.xml', 'tests/data/etc/decoders/subpath'),
    ('test3_decoders.xml', 'tests/data/etc/decoders/subpath/'),
])
def test_delete_decoder_file(filename, relative_dirname):
    """Test deleting a decoder file."""
    with patch('securics.decoder.exists', return_value=True):
        # Assert returned type is AffectedItemsSecuricsResult when everything is correct
        with patch('securics.decoder.remove'):
            assert(isinstance(decoder.delete_decoder_file(filename=filename, 
                                                          relative_dirname=relative_dirname),
                                                          AffectedItemsSecuricsResult))


def test_delete_decoder_file_ko():
    """Test exceptions on delete method."""
    # Assert error code when remove() method returns IOError
    with patch('securics.decoder.exists', return_value=True):
        with patch('securics.decoder.remove', side_effect=IOError()):
            result = decoder.delete_decoder_file(filename='file')
            assert isinstance(result, AffectedItemsSecuricsResult), 'No expected result type'
            assert result.render()['data']['failed_items'][0]['error']['code'] == 1907,\
                'Error code not expected.'

    # Assert error code when decoder does not exist
    result = decoder.delete_decoder_file(filename='file')
    assert isinstance(result, AffectedItemsSecuricsResult), 'No expected result type'
    assert result.render()['data']['failed_items'][0]['error']['code'] == 1906,\
        'Error code not expected.'

    # Assert error code passing invalid relative_dirname
    result = decoder.delete_decoder_file(filename='test_decoder.xml',
                                            relative_dirname='etc/not_exists')
    assert isinstance(result, AffectedItemsSecuricsResult), 'No expected result type'
    assert result.render()['data']['failed_items'][0]['error']['code'] == 1505,\
        'Error code not expected.'

    # Assert error code when decoder file is in default ruleset
    result = decoder.delete_decoder_file(filename='test1_decoder.xml',
                                         relative_dirname='tests/data/decoders')
    assert isinstance(result, AffectedItemsSecuricsResult), 'No expected result type'
    assert result.render()['data']['failed_items'][0]['error']['code'] == 1506,\
        'Error code not expected.'
