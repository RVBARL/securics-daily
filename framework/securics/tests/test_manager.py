#!/usr/bin/env python
# Copyright (C) 2023-2024, RV Bionics Group SpA.
# Created by Securics, Inc. <info@rvbionics.com>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

import json
import operator
import os
import socket
import sys
from unittest.mock import patch, MagicMock

import pytest

with patch('securics.core.common.securics_uid'):
    with patch('securics.core.common.securics_gid'):
        sys.modules['securics.rbac.orm'] = MagicMock()
        import securics.rbac.decorators
        from securics.tests.util import RBAC_bypasser

        del sys.modules['securics.rbac.orm']
        securics.rbac.decorators.expose_resources = RBAC_bypasser

        from securics.manager import *
        from securics.core.manager import LoggingFormat
        from securics.core.tests.test_manager import get_logs
        from securics import SecuricsInternalError

test_data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')


@pytest.fixture(scope='module', autouse=True)
def mock_securics_path():
    with patch('securics.core.common.SECURICS_PATH', new=test_data_path):
        yield


class InitManager:
    def __init__(self):
        """Sets up necessary environment to test manager functions"""
        # path for temporary API files
        self.api_tmp_path = os.path.join(test_data_path, 'tmp')
        # rules
        self.input_rules_file = 'test_rules.xml'
        self.output_rules_file = 'uploaded_test_rules.xml'
        # decoders
        self.input_decoders_file = 'test_decoders.xml'
        self.output_decoders_file = 'uploaded_test_decoders.xml'
        # CDB lists
        self.input_lists_file = 'test_lists'
        self.output_lists_file = 'uploaded_test_lists'


@pytest.fixture(scope='module')
def test_manager():
    # Set up
    test_manager = InitManager()
    return test_manager


manager_status = {'securics-agentlessd': 'running', 'securics-analysisd': 'running', 'securics-authd': 'running',
 'securics-csyslogd': 'running', 'securics-dbd': 'running', 'securics-monitord': 'running',
 'securics-execd': 'running', 'securics-integratord': 'running', 'securics-logcollector': 'running',
 'securics-maild': 'running', 'securics-remoted': 'running', 'securics-reportd': 'running',
 'securics-syscheckd': 'running', 'securics-clusterd': 'running', 'securics-modulesd': 'running',
 'securics-db': 'running', 'securics-apid': 'running'}


@patch('securics.core.manager.status', return_value=manager_status)
def test_get_status(mock_status):
    """Tests get_status() function works"""
    result = get_status()

    # Assert there are no errors and type returned
    assert isinstance(result, AffectedItemsSecuricsResult), 'No expected result type'
    assert result.render()['data']['total_failed_items'] == 0


@pytest.mark.parametrize('tag, level, total_items, sort_by, sort_ascending', [
    (None, None, 13, None, None),
    ('securics-modulesd:database', None, 2, None, None),
    ('securics-modulesd:syscollector', None, 2, None, None),
    ('securics-modulesd:syscollector', None, 2, None, None),
    ('securics-modulesd:aws-s3', None, 5, None, None),
    ('securics-execd', None, 1, None, None),
    ('securics-csyslogd', None, 2, None, None),
    ('random', None, 0, ['timestamp'], True),
    (None, 'info', 7, ['timestamp'], False),
    (None, 'error', 2, ['level'], True),
    (None, 'debug', 2, ['level'], False),
    (None, None, 13, ['tag'], True),
    (None, 'random', 0, None, True),
    (None, 'warning', 2, None, False)
])
@patch("securics.core.manager.get_securics_active_logging_format", return_value=LoggingFormat.plain)
@patch("securics.core.manager.exists", return_value=True)
def test_ossec_log(mock_exists, mock_active_logging_format, tag, level, total_items, sort_by, sort_ascending):
    """Test reading ossec.log file contents.

    Parameters
    ----------
    level : str
        Filters by log type: all, error or info.
    tag : str
        Filters by log category (i.e. securics-remoted).
    total_items : int
        Expected items to be returned after calling ossec_log.
    sort_by : list
        Fields to sort the items by.
    sort_ascending : boolean
        Sort in ascending (true) or descending (false) order.
    """
    with patch('securics.core.manager.tail') as tail_patch:
        # Return ossec_log_file when calling tail() method
        ossec_log_file = get_logs()
        tail_patch.return_value = ossec_log_file.splitlines()

        result = ossec_log(level=level, tag=tag, sort_by=sort_by, sort_ascending=sort_ascending)

        # Assert type, number of items and presence of trailing characters
        assert isinstance(result, AffectedItemsSecuricsResult), 'No expected result type'
        assert result.render()['data']['total_affected_items'] == total_items
        assert all(log['description'][-1] != '\n' for log in result.render()['data']['affected_items'])
        if tag is not None and level != 'securics-modulesd:syscollector':
            assert all('\n' not in log['description'] for log in result.render()['data']['affected_items'])
        if sort_by:
            reversed_result = ossec_log(level=level, tag=tag, sort_by=sort_by, sort_ascending=not sort_ascending)
            for i in range(total_items):
                assert result.render()['data']['affected_items'][i][sort_by[0]] == \
                       reversed_result.render()['data']['affected_items'][total_items - 1 - i][sort_by[0]]


@pytest.mark.parametrize('q, field, operation, values', [
    ('level=debug,level=error', 'level', 'OR', 'debug, error'),
    ('timestamp=2019/03/26 19:49:15', 'timestamp', '=', '2019/03/26T19:49:15Z'),
    ('timestamp<2019/03/26 19:49:14', 'timestamp', '<', '2019/03/26T19:49:15Z'),
])
@patch("securics.core.manager.get_securics_active_logging_format", return_value=LoggingFormat.plain)
@patch("securics.core.manager.exists", return_value=True)
def test_ossec_log_q(mock_exists, mock_active_logging_format, q, field, operation, values):
    """Check that the 'q' parameter is working correctly.

    Parameters
    ----------
    q : str
        Query to execute.
    field : str
        Field affected by the query.
    operation : str
        Operation type to be performed in the query.
    values : str
        Values used for the comparison.
    """
    with patch('securics.core.manager.tail') as tail_patch:
        ossec_log_file = get_logs()
        tail_patch.return_value = ossec_log_file.splitlines()

        result = ossec_log(q=q)

        if operation != 'OR':
            operators = {'=': operator.eq, '!=': operator.ne, '<': operator.lt, '>': operator.gt}
            assert all(operators[operation](log[field], values) for log in result.render()['data']['affected_items'])
        else:
            assert all(log[field] in values for log in result.render()['data']['affected_items'])


@patch("securics.core.manager.get_securics_active_logging_format", return_value=LoggingFormat.plain)
@patch("securics.core.manager.exists", return_value=True)
def test_ossec_log_summary(mock_exists, mock_active_logging_format):
    """Tests ossec_log_summary function works and returned data match with expected"""
    expected_result = {
        'securics-csyslogd': {'all': 2, 'info': 2, 'error': 0, 'critical': 0, 'warning': 0, 'debug': 0},
        'securics-execd': {'all': 1, 'info': 0, 'error': 1, 'critical': 0, 'warning': 0, 'debug': 0},
        'securics-modulesd:aws-s3': {'all': 5, 'info': 2, 'error': 1, 'critical': 0, 'warning': 2, 'debug': 0},
        'securics-modulesd:database': {'all': 2, 'info': 0, 'error': 0, 'critical': 0, 'warning': 0, 'debug': 2},
        'securics-modulesd:syscollector': {'all': 2, 'info': 2, 'error': 0, 'critical': 0, 'warning': 0, 'debug': 0},
        'securics-rootcheck': {'all': 1, 'info': 1, 'error': 0, 'critical': 0, 'warning': 0, 'debug': 0}
    }

    logs = get_logs().splitlines()
    with patch('securics.core.manager.tail', return_value=logs):
        result = ossec_log_summary()

        # Assert data match what was expected and type of the result.
        assert isinstance(result, AffectedItemsSecuricsResult), 'No expected result type'
        assert result.render()['data']['total_affected_items'] == 6
        assert all(all(value == expected_result[key] for key, value in item.items())
                   for item in result.render()['data']['affected_items'])


def test_get_api_config():
    """Checks that get_api_config method is returning current api_conf dict."""
    result = get_api_config().render()

    assert 'node_api_config' in result['data']['affected_items'][0], 'node_api_config key not found in result'
    assert result['data']['affected_items'][0]['node_name'] == 'manager', 'Not expected node name'


@patch('socket.socket')
@patch('securics.core.cluster.utils.fcntl')
@patch('securics.core.cluster.utils.open')
@patch('os.path.exists', return_value=True)
def test_restart_ok(mock_exists, mock_path, mock_fcntl, mock_socket):
    """Tests restarting a manager"""
    result = restart()

    # Assert there are no errors and type of the result.
    assert isinstance(result, AffectedItemsSecuricsResult), 'No expected result type'
    assert result.render()['data']['total_failed_items'] == 0


@patch('securics.core.cluster.utils.open')
@patch('securics.core.cluster.utils.fcntl')
@patch('os.path.exists', return_value=False)
def test_restart_ko_socket(mock_exists, mock_fcntl, mock_open):
    """Tests restarting a manager exceptions"""

    # Socket path not exists
    with pytest.raises(SecuricsInternalError, match='.* 1901 .*'):
        restart()

    # Socket error
    with patch("os.path.exists", return_value=True):
        with patch('socket.socket', side_effect=socket.error):
            with pytest.raises(SecuricsInternalError, match='.* 1902 .*'):
                restart()

        with patch('socket.socket.connect'):
            with patch('socket.socket.send', side_effect=socket.error):
                with pytest.raises(SecuricsInternalError, match='.* 1014 .*'):
                    restart()


@pytest.mark.parametrize('error_flag, error_msg', [
    (0, ""),
    (1, "2019/02/27 11:30:07 securics-clusterd: ERROR: [Cluster] [Main] Error 3004 - Error in cluster configuration: "
        "Unspecified key"),
    (1, "2019/02/27 11:30:24 securics-authd: ERROR: (1230): Invalid element in the configuration: "
        "'use_source_i'.\n2019/02/27 11:30:24 securics-authd: ERROR: (1202): Configuration error at "
        "'/var/ossec/etc/ossec.conf'.")
])
@patch("securics.core.manager.exists", return_value=True)
def test_validation(mock_exists, error_flag, error_msg):
    """Test validation() method works as expected

    Tests configuration validation function with multiple scenarios:
        * No errors found in configuration
        * Error found in cluster configuration
        * Error found in any other configuration

    Parameters
    ----------
    error_flag : int
        Error flag to be mocked in the socket response.
    error_msg : str
        Error message to be mocked in the socket response.
    """
    with patch('securics.core.manager.SecuricsSocket') as sock:
        # Mock sock response
        json_response = json.dumps({'error': error_flag, 'message': error_msg}).encode()
        sock.return_value.receive.return_value = json_response
        result = validation()

        # Assert if error was returned
        assert isinstance(result, AffectedItemsSecuricsResult), 'No expected result type'
        assert result.render()['data']['total_failed_items'] == error_flag


@pytest.mark.parametrize('exception', [
    SecuricsInternalError(1013),
    SecuricsError(1013)
])
@patch('securics.manager.validate_ossec_conf')
def test_validation_ko(mock_validate, exception):
    mock_validate.side_effect = exception

    if isinstance(exception, SecuricsInternalError):
        with pytest.raises(SecuricsInternalError, match='.* 1013 .*'):
            validation()
    else:
        result = validation()
        assert not result.affected_items
        assert result.total_failed_items == 1


@patch('securics.core.configuration.get_active_configuration')
def test_get_config(mock_act_conf):
    """Tests get_config() method works as expected"""
    get_config('component', 'config')

    # Assert whether get_active_configuration() method receives the expected parameters.
    mock_act_conf.assert_called_once_with(agent_id='000', component='component', configuration='config')


def test_get_config_ko():
    """Tests get_config() function returns an error"""
    result = get_config()

    assert isinstance(result, AffectedItemsSecuricsResult), 'No expected result type'
    assert result.render()['data']['failed_items'][0]['error']['code'] == 1307


@pytest.mark.parametrize('raw', [True, False])
def test_read_ossec_conf(raw):
    """Tests read_ossec_conf() function works as expected"""
    result = read_ossec_conf(raw=raw)

    if raw:
        assert isinstance(result, str), 'No expected result type'
    else:
        assert isinstance(result, AffectedItemsSecuricsResult), 'No expected result type'
        assert result.render()['data']['total_failed_items'] == 0


def test_read_ossec_con_ko():
    """Tests read_ossec_conf() function returns an error"""
    result = read_ossec_conf(section='test')

    assert isinstance(result, AffectedItemsSecuricsResult), 'No expected result type'
    assert result.render()['data']['failed_items'][0]['error']['code'] == 1102

@patch('builtins.open')
def test_get_basic_info(mock_open):
    """Tests get_basic_info() function works as expected"""
    result = get_basic_info()

    assert isinstance(result, AffectedItemsSecuricsResult), 'No expected result type'
    assert result.render()['data']['total_failed_items'] == 0


@patch('securics.manager.validate_ossec_conf', return_value={'status': 'OK'})
@patch('securics.manager.write_ossec_conf')
@patch('securics.manager.validate_securics_xml')
@patch('securics.manager.full_copy')
@patch('securics.manager.exists', return_value=True)
@patch('securics.manager.remove')
@patch('securics.manager.safe_move')
def test_update_ossec_conf(move_mock, remove_mock, exists_mock, full_copy_mock, prettify_mock, write_mock,
                           validate_mock):
    """Test update_ossec_conf works as expected."""
    result = update_ossec_conf(new_conf="placeholder config")
    write_mock.assert_called_once()
    assert isinstance(result, AffectedItemsSecuricsResult), 'No expected result type'
    assert result.render()['data']['total_failed_items'] == 0
    remove_mock.assert_called_once()


@pytest.mark.parametrize('new_conf', [
    None,
    "invalid configuration"
])
@patch('securics.manager.validate_ossec_conf')
@patch('securics.manager.write_ossec_conf')
@patch('securics.manager.validate_securics_xml')
@patch('securics.manager.full_copy')
@patch('securics.manager.exists', return_value=True)
@patch('securics.manager.remove')
@patch('securics.manager.safe_move')
def test_update_ossec_conf_ko(move_mock, remove_mock, exists_mock, full_copy_mock, prettify_mock, write_mock,
                              validate_mock, new_conf):
    """Test update_ossec_conf() function return an error and restore the configuration if the provided configuration
    is not valid."""
    result = update_ossec_conf(new_conf=new_conf)
    assert isinstance(result, AffectedItemsSecuricsResult), 'No expected result type'
    assert result.render()['data']['failed_items'][0]['error']['code'] == 1125
    move_mock.assert_called_once()
