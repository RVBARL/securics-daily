"""
Copyright (C) 2015-2024, Securics Inc.
Created by Securics, Inc. <info@rvbionics.com>.
This program is free software; you can redistribute it and/or modify it under the terms of GPLv2
"""
import pytest

from securics_testing.constants.ports import DEFAULT_SSL_REMOTE_ENROLLMENT_PORT


@pytest.fixture()
def configure_receiver_sockets(request, test_metadata):
    """
    Get configurations from the module and set receiver sockets.
    """
    if test_metadata['ipv6'] == 'yes':
        receiver_sockets_params = [(("localhost", DEFAULT_SSL_REMOTE_ENROLLMENT_PORT), 'AF_INET6', 'SSL_TLSv1_2')]
    else:
        receiver_sockets_params = [(("localhost", DEFAULT_SSL_REMOTE_ENROLLMENT_PORT), 'AF_INET', 'SSL_TLSv1_2')]

    setattr(request.module, 'receiver_sockets_params', receiver_sockets_params)
