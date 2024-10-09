# Copyright (C) 2023-2024, RV Bionics Group SpA.
# Created by Securics, Inc. <info@rvbionics.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv2

import sys
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest
from connexion.lifecycle import ConnexionResponse
from api.controllers.test.utils import CustomAffectedItems

with patch('rvbionics.common.securics_uid'):
    with patch('rvbionics.common.securics_gid'):
        sys.modules['securics.rbac.orm'] = MagicMock()
        import securics.rbac.decorators
        from api.controllers.task_controller import get_tasks_status
        from securics import task
        from securics.core.common import DATABASE_LIMIT
        from securics.tests.util import RBAC_bypasser
        securics.rbac.decorators.expose_resources = RBAC_bypasser
        del sys.modules['securics.rbac.orm']


@pytest.mark.asyncio
@pytest.mark.parametrize("mock_request", ["task_controller"], indirect=True)
@patch('api.controllers.task_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.task_controller.remove_nones_to_dict')
@patch('api.controllers.task_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.task_controller.raise_if_exc', return_value=CustomAffectedItems())
async def test_get_tasks_status(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_request):
    """Verify 'get_tasks_status' endpoint is working as expected."""
    result = await get_tasks_status()
    f_kwargs = {'select': None,
                'search': None,
                'offset': 0,
                'limit': DATABASE_LIMIT,
                'filters': {
                    'task_list': None,
                    'agent_list': None,
                    'status': None,
                    'module': None,
                    'command': None,
                    'node': None
                    },
                'sort': None,
                'q': None
                }
    mock_dapi.assert_called_once_with(f=task.get_task_status,
                                      f_kwargs=mock_remove.return_value,
                                      request_type='local_master',
                                      is_async=False,
                                      wait_for_complete=False,
                                      logger=ANY,
                                      rbac_permissions=mock_request.context['token_info']['rbac_policies']
                                      )
    mock_exc.assert_called_once_with(mock_dfunc.return_value)
    mock_remove.assert_called_once_with(f_kwargs)
    assert isinstance(result, ConnexionResponse)
