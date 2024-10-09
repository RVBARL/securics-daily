# Copyright (C) 2023-2024, RV Bionics Group SpA.
# Created by Securics, Inc. <info@rvbionics.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv2

import json
from contextvars import ContextVar
from grp import getgrnam
from pwd import getpwnam
from unittest.mock import patch

import pytest

from securics.core.common import find_securics_path, securics_uid, securics_gid, context_cached, reset_context_cache, \
    get_context_cache


@pytest.mark.parametrize('fake_path, expected', [
    ('/var/ossec/framework/python/lib/python3.7/site-packages/securics-3.10.0-py3.7.egg/securics', '/var/ossec'),
    ('/my/custom/path/framework/python/lib/python3.7/site-packages/securics-3.10.0-py3.7.egg/securics', '/my/custom/path'),
    ('/my/fake/path', '')
])
def test_find_securics_path(fake_path, expected):
    with patch('securics.core.common.__file__', new=fake_path):
        assert (find_securics_path.__wrapped__() == expected)


def test_find_securics_path_relative_path():
    with patch('os.path.abspath', return_value='~/framework'):
        assert (find_securics_path.__wrapped__() == '~')


def test_securics_uid():
    with patch('securics.core.common.getpwnam', return_value=getpwnam("root")):
        securics_uid()


def test_securics_gid():
    with patch('securics.core.common.getgrnam', return_value=getgrnam("root")):
        securics_gid()


def test_context_cached():
    """Verify that context_cached decorator correctly saves and returns saved value when called again."""

    test_context_cached.calls_to_foo = 0

    @context_cached('foobar')
    def foo(arg='bar', **data):
        test_context_cached.calls_to_foo += 1
        return arg

    # The result of function 'foo' is being cached and it has been called once
    assert foo() == 'bar' and test_context_cached.calls_to_foo == 1, '"bar" should be returned with 1 call to foo.'
    assert foo() == 'bar' and test_context_cached.calls_to_foo == 1, '"bar" should be returned with 1 call to foo.'
    assert isinstance(get_context_cache()[json.dumps({"key": "foobar", "args": [], "kwargs": {}})], ContextVar)

    # foo called with an argument
    assert foo('other_arg') == 'other_arg' and test_context_cached.calls_to_foo == 2, '"other_arg" should be ' \
                                                                                      'returned with 2 calls to foo. '
    assert isinstance(get_context_cache()[json.dumps({"key": "foobar", "args": ['other_arg'], "kwargs": {}})],
                      ContextVar)

    # foo called with the same argument as default, a new context var is created in the cache
    assert foo('bar') == 'bar' and test_context_cached.calls_to_foo == 3, '"bar" should be returned with 3 calls to ' \
                                                                          'foo. '
    assert isinstance(get_context_cache()[json.dumps({"key": "foobar", "args": ['bar'], "kwargs": {}})], ContextVar)

    # Reset cache and calls to foo
    reset_context_cache()
    test_context_cached.calls_to_foo = 0

    # foo called with kwargs, a new context var is created with kwargs not empty
    assert foo(data='bar') == 'bar' and test_context_cached.calls_to_foo == 1, '"bar" should be returned with 1 ' \
                                                                               'calls to foo. '
    assert isinstance(get_context_cache()[json.dumps({"key": "foobar", "args": [], "kwargs": {"data": "bar"}})],
                      ContextVar)


@patch('securics.core.logtest.create_securics_socket_message', side_effect=SystemExit)
def test_origin_module_context_var_framework(mock_create_socket_msg):
    """Test that the origin_module context variable is being set to framework."""
    from securics import logtest

    # side_effect used to avoid mocking the rest of functions
    with pytest.raises(SystemExit):
        logtest.run_logtest()

    assert mock_create_socket_msg.call_args[1]['origin']['module'] == 'framework'


@pytest.mark.asyncio
@patch('securics.core.logtest.create_securics_socket_message', side_effect=SystemExit)
@patch('securics.core.cluster.dapi.dapi.DistributedAPI.check_securics_status', side_effect=None)
async def test_origin_module_context_var_api(mock_check_securics_status, mock_create_socket_msg):
    """Test that the origin_module context variable is being set to API."""
    import logging
    from securics.core.cluster.dapi import dapi
    from securics import logtest

    # side_effect used to avoid mocking the rest of functions
    with pytest.raises(SystemExit):
        d = dapi.DistributedAPI(f=logtest.run_logtest, logger=logging.getLogger('securics'), is_async=True)
        await d.distribute_function()

    assert mock_create_socket_msg.call_args[1]['origin']['module'] == 'API'
