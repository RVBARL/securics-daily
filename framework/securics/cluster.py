# Copyright (C) 2023-2024, RV Bionics Group SpA.
# Created by Securics, Inc. <info@rvbionics.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv2

from typing import Union

from securics.core import common
from securics.core.cluster import local_client
from securics.core.cluster.cluster import get_node
from securics.core.cluster.control import get_health, get_nodes, get_node_ruleset_integrity
from securics.core.cluster.utils import get_cluster_status, read_cluster_config, read_config
from securics.core.exception import SecuricsError, SecuricsResourceNotFound
from securics.core.results import AffectedItemsSecuricsResult, SecuricsResult
from securics.rbac.decorators import expose_resources, async_list_handler

cluster_enabled = not read_cluster_config(from_import=True)['disabled']
node_id = get_node().get('node') if cluster_enabled else None


@expose_resources(actions=['cluster:read'], resources=[f'node:id:{node_id}'])
def read_config_wrapper() -> AffectedItemsSecuricsResult:
    """Wrapper for read_config.

    Returns
    -------
    AffectedItemsSecuricsResult
        Affected items.
    """
    result = AffectedItemsSecuricsResult(all_msg='All selected information was returned',
                                      none_msg='No information was returned'
                                      )
    try:
        result.affected_items.append(read_config())
    except SecuricsError as e:
        result.add_failed_item(id_=node_id, error=e)
    result.total_affected_items = len(result.affected_items)

    return result


@expose_resources(actions=['cluster:read'], resources=[f'node:id:{node_id}'])
def get_node_wrapper() -> AffectedItemsSecuricsResult:
    """Wrapper for get_node.

    Returns
    -------
    AffectedItemsSecuricsResult
        Affected items.
    """
    result = AffectedItemsSecuricsResult(all_msg='All selected information was returned',
                                      none_msg='No information was returned'
                                      )
    try:
        result.affected_items.append(get_node())
    except SecuricsError as e:
        result.add_failed_item(id_=node_id, error=e)
    result.total_affected_items = len(result.affected_items)

    return result


@expose_resources(actions=['cluster:status'], resources=['*:*:*'], post_proc_func=None)
def get_status_json() -> SecuricsResult:
    """Return the cluster status.

    Returns
    -------
    SecuricsResult
        SecuricsResult object with the cluster status.
    """
    return SecuricsResult({'data': get_cluster_status()})


@expose_resources(actions=['cluster:read'], resources=['node:id:{filter_node}'], post_proc_func=async_list_handler)
async def get_health_nodes(lc: local_client.LocalClient,
                           filter_node: Union[str, list] = None) -> AffectedItemsSecuricsResult:
    """Wrapper for get_health.

    Parameters
    ----------
    lc : LocalClient object
        LocalClient with which to send the 'get_nodes' request.
    filter_node : str or list
        Node to return.

    Returns
    -------
    AffectedItemsSecuricsResult
        Affected items.
    """
    result = AffectedItemsSecuricsResult(all_msg='All selected nodes healthcheck information was returned',
                                      some_msg='Some nodes healthcheck information was not returned',
                                      none_msg='No healthcheck information was returned'
                                      )

    data = await get_health(lc, filter_node=filter_node)
    for v in data['nodes'].values():
        result.affected_items.append(v)

    result.affected_items = sorted(result.affected_items, key=lambda i: i['info']['name'])
    result.total_affected_items = len(result.affected_items)

    return result


@expose_resources(actions=['cluster:read'], resources=['node:id:{filter_node}'], post_proc_func=async_list_handler)
async def get_nodes_info(lc: local_client.LocalClient, filter_node: Union[str, list] = None,
                         **kwargs: dict) -> AffectedItemsSecuricsResult:
    """Wrapper for get_nodes.

    Parameters
    ----------
    lc : LocalClient object
        LocalClient with which to send the 'get_nodes' request.
    filter_node : str or list
        Node to return.

    Returns
    -------
    AffectedItemsSecuricsResult
        Affected items.
    """
    result = AffectedItemsSecuricsResult(all_msg='All selected nodes information was returned',
                                      some_msg='Some nodes information was not returned',
                                      none_msg='No information was returned'
                                      )

    nodes = set(filter_node).intersection(set(common.cluster_nodes.get()))
    non_existent_nodes = set(filter_node) - nodes
    data = await get_nodes(lc, filter_node=list(nodes), **kwargs)
    for item in data['items']:
        result.affected_items.append(item)

    for node in non_existent_nodes:
        result.add_failed_item(id_=node, error=SecuricsResourceNotFound(1730))
    result.total_affected_items = data['totalItems']

    return result


@expose_resources(actions=['cluster:read'], resources=[f"node:id:{node_id}"],
                  post_proc_func=async_list_handler)
async def get_ruleset_sync_status(master_md5: dict = None):
    """Compare node's md5 with the master node's to check the custom ruleset synchronization status.

    Parameters
    ----------
    master_md5 : dict
        Master node's ruleset integrity.

    Returns
    -------
    AffectedItemsSecuricsResult
        Result with current node's custom ruleset integrity.
    """
    result = AffectedItemsSecuricsResult(all_msg="Nodes ruleset synchronization status was successfully read",
                                      some_msg="Could not read ruleset synchronization status in some nodes",
                                      none_msg="Could not read ruleset synchronization status",
                                      sort_casting=["str"]
                                      )

    try:
        lc = local_client.LocalClient()
        node_ruleset_integrity = await get_node_ruleset_integrity(lc)
    except SecuricsError as e:
        result.add_failed_item(id_=node_id, error=e)
    else:
        result.affected_items.append({'name': node_id,
                                      'synced': master_md5 == node_ruleset_integrity})
    result.total_affected_items = len(result.affected_items)

    return result
