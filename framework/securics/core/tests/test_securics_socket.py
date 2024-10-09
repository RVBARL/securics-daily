# Copyright (C) 2023-2024, RV Bionics Group SpA.
# Created by Securics, Inc. <info@rvbionics.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv2

from unittest.mock import patch, MagicMock

import pytest

from securics.core.exception import SecuricsException
from securics.core.securics_socket import SecuricsSocket, SecuricsSocketJSON, SOCKET_COMMUNICATION_PROTOCOL_VERSION, \
    create_securics_socket_message


@patch('securics.core.securics_socket.SecuricsSocket._connect')
def test_SecuricsSocket__init__(mock_conn):
    """Tests SecuricsSocket.__init__ function works"""

    SecuricsSocket('test_path')

    mock_conn.assert_called_once_with()


@patch('securics.core.securics_socket.socket.socket.connect')
def test_SecuricsSocket_protected_connect(mock_conn):
    """Tests SecuricsSocket._connect function works"""

    SecuricsSocket('test_path')

    mock_conn.assert_called_with('test_path')


@patch('securics.core.securics_socket.socket.socket.connect', side_effect=Exception)
def test_SecuricsSocket_protected_connect_ko(mock_conn):
    """Tests SecuricsSocket._connect function exceptions works"""

    with pytest.raises(SecuricsException, match=".* 1013 .*"):
        SecuricsSocket('test_path')


@patch('securics.core.securics_socket.socket.socket.connect')
@patch('securics.core.securics_socket.socket.socket.close')
def test_SecuricsSocket_close(mock_close, mock_conn):
    """Tests SecuricsSocket.close function works"""

    queue = SecuricsSocket('test_path')

    queue.close()

    mock_conn.assert_called_once_with('test_path')
    mock_close.assert_called_once_with()


@patch('securics.core.securics_socket.socket.socket.connect')
@patch('securics.core.securics_socket.socket.socket.send')
def test_SecuricsSocket_send(mock_send, mock_conn):
    """Tests SecuricsSocket.send function works"""

    queue = SecuricsSocket('test_path')

    response = queue.send(b"\x00\x01")

    assert isinstance(response, MagicMock)
    mock_conn.assert_called_once_with('test_path')


@pytest.mark.parametrize('msg, effect, send_effect, expected_exception', [
    ('text_msg', 'side_effect', None, 1105),
    (b"\x00\x01", 'return_value', 0, 1014),
    (b"\x00\x01", 'side_effect', Exception, 1014)
])
@patch('securics.core.securics_socket.socket.socket.connect')
def test_SecuricsSocket_send_ko(mock_conn, msg, effect, send_effect, expected_exception):
    """Tests SecuricsSocket.send function exceptions works"""

    queue = SecuricsSocket('test_path')

    if effect == 'return_value':
        with patch('securics.core.securics_socket.socket.socket.send', return_value=send_effect):
            with pytest.raises(SecuricsException, match=f'.* {expected_exception} .*'):
                queue.send(msg)
    else:
        with patch('securics.core.securics_socket.socket.socket.send', side_effect=send_effect):
            with pytest.raises(SecuricsException, match=f'.* {expected_exception} .*'):
                queue.send(msg)

    mock_conn.assert_called_once_with('test_path')


@patch('securics.core.securics_socket.socket.socket.connect')
@patch('securics.core.securics_socket.unpack', return_value='1024')
@patch('securics.core.securics_socket.socket.socket.recv')
def test_SecuricsSocket_receive(mock_recv, mock_unpack, mock_conn):
    """Tests SecuricsSocket.receive function works"""

    queue = SecuricsSocket('test_path')

    response = queue.receive()

    assert isinstance(response, MagicMock)
    mock_conn.assert_called_once_with('test_path')


@patch('securics.core.securics_socket.socket.socket.connect')
@patch('securics.core.securics_socket.socket.socket.recv', side_effect=Exception)
def test_SecuricsSocket_receive_ko(mock_recv, mock_conn):
    """Tests SecuricsSocket.receive function exception works"""

    queue = SecuricsSocket('test_path')

    with pytest.raises(SecuricsException, match=".* 1014 .*"):
        queue.receive()

    mock_conn.assert_called_once_with('test_path')


@patch('securics.core.securics_socket.SecuricsSocket._connect')
def test_SecuricsSocketJSON__init__(mock_conn):
    """Tests SecuricsSocketJSON.__init__ function works"""

    SecuricsSocketJSON('test_path')

    mock_conn.assert_called_once_with()


@patch('securics.core.securics_socket.socket.socket.connect')
@patch('securics.core.securics_socket.SecuricsSocket.send')
def test_SecuricsSocketJSON_send(mock_send, mock_conn):
    """Tests SecuricsSocketJSON.send function works"""

    queue = SecuricsSocketJSON('test_path')

    response = queue.send('test_msg')

    assert isinstance(response, MagicMock)
    mock_conn.assert_called_once_with('test_path')


@pytest.mark.parametrize('raw', [
    True, False
])
@patch('securics.core.securics_socket.socket.socket.connect')
@patch('securics.core.securics_socket.SecuricsSocket.receive')
@patch('securics.core.securics_socket.loads', return_value={'error':0, 'message':None, 'data':'Ok'})
def test_SecuricsSocketJSON_receive(mock_loads, mock_receive, mock_conn, raw):
    """Tests SecuricsSocketJSON.receive function works"""
    queue = SecuricsSocketJSON('test_path')
    response = queue.receive(raw=raw)
    if raw:
        assert isinstance(response, dict)
    else:
        assert isinstance(response, str)
    mock_conn.assert_called_once_with('test_path')


@patch('securics.core.securics_socket.socket.socket.connect')
@patch('securics.core.securics_socket.SecuricsSocket.receive')
@patch('securics.core.securics_socket.loads', return_value={'error':10000, 'message':'Error', 'data':'KO'})
def test_SecuricsSocketJSON_receive_ko(mock_loads, mock_receive, mock_conn):
    """Tests SecuricsSocketJSON.receive function works"""

    queue = SecuricsSocketJSON('test_path')

    with pytest.raises(SecuricsException, match=".* 10000 .*"):
        queue.receive()

    mock_conn.assert_called_once_with('test_path')


@pytest.mark.parametrize('origin, command, parameters', [
    ('origin_sample', 'command_sample', {'sample': 'sample'}),
    (None, 'command_sample', {'sample': 'sample'}),
    ('origin_sample', None, {'sample': 'sample'}),
    ('origin_sample', 'command_sample', None),
    (None, None, None)
])
def test_create_securics_socket_message(origin, command, parameters):
    """Test create_securics_socket_message function."""
    response_message = create_securics_socket_message(origin, command, parameters)
    assert response_message['version'] == SOCKET_COMMUNICATION_PROTOCOL_VERSION
    assert response_message.get('origin') == origin
    assert response_message.get('command') == command
    assert response_message.get('parameters') == parameters
