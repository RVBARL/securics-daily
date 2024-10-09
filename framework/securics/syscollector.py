# Copyright (C) 2023-2024, RV Bionics Group SpA.
# Created by Securics, Inc. <info@rvbionics.com>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

from securics.core import common
from securics.core.agent import get_agents_info
from securics.core.exception import SecuricsResourceNotFound
from securics.core.results import AffectedItemsSecuricsResult, merge
from securics.core.syscollector import SecuricsDBQuerySyscollector, get_valid_fields, Type
from securics.rbac.decorators import expose_resources


@expose_resources(actions=['syscollector:read'], resources=['agent:id:{agent_list}'])
def get_item_agent(agent_list: list, offset: int = 0, limit: int = common.DATABASE_LIMIT, select: dict = None,
                   search: dict = None, sort: dict = None, filters: dict = None, q: str = '', array: bool = True,
                   nested: bool = True, element_type: str = 'os', distinct: bool = False) -> AffectedItemsSecuricsResult:
    """Get syscollector information about a list of agents.

    Parameters
    ----------
    agent_list : list
        List containing the agent ID.
    filters : dict
        Fields to filter by.
    offset : int
        First item to return.
    limit : int
        Maximum number of items to return.
    sort : dict
        Sorts the items. Format: {"fields":["field1","field2"],"order":"asc|desc"}.
    search : dict
        Looks for items with the specified string. Format: {"fields": ["field1","field2"]}
    select : dict
        Select fields to return. Format: {"fields":["field1","field2"]}.
    q : str
        Query to filter by.
    nested : bool
        Specify whether there are nested fields or not.
    element_type : str
        Type of element to get syscollector information from. Default: 'os'
    array : bool
        Array.
    distinct : bool
        Look for distinct values.

    Returns
    -------
    AffectedItemsSecuricsResult
        Syscollector information.
    """
    result = AffectedItemsSecuricsResult(
        none_msg='No syscollector information was returned',
        some_msg='Some syscollector information was not returned',
        all_msg='All specified syscollector information was returned',
        sort_fields=['agent_id'] if sort is None else sort['fields'],
        sort_casting=['str'],
        sort_ascending=[sort['order'] == 'asc' for _ in sort['fields']] if sort is not None else ['True']
    )

    system_agents = get_agents_info()
    for agent in agent_list:
        try:
            if agent not in system_agents:
                raise SecuricsResourceNotFound(1701)
            table, valid_select_fields = get_valid_fields(Type(element_type), agent_id=agent)
            with SecuricsDBQuerySyscollector(agent_id=agent, offset=offset, limit=limit, select=select,
                                          search=search,
                                          sort=sort, filters=filters, fields=valid_select_fields, table=table,
                                          array=array, nested=nested, query=q, distinct=distinct) as db_query:
                data = db_query.run()

            for item in data['items']:
                item['agent_id'] = agent
                result.affected_items.append(item)
            result.total_affected_items += data['totalItems']
        except SecuricsResourceNotFound as e:
            result.add_failed_item(id_=agent, error=e)

    # Avoid that integer type fields are casted to string, this prevents sort parameter malfunctioning
    try:
        if len(result.affected_items) and sort and len(sort['fields']) == 1:
            fields = sort['fields'][0].split('.')
            element = result.affected_items[0][fields.pop(0)]
            for field in fields:
                element = element[field]
            element_type = type(element).__name__
            result.sort_casting = [element_type] if element_type not in ['str', 'datetime'] else ['str']
    except KeyError:
        pass

    result.affected_items = merge(*[[res] for res in result.affected_items],
                                  criteria=result.sort_fields,
                                  ascending=result.sort_ascending,
                                  types=result.sort_casting)

    return result
