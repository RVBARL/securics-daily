/* Copyright (C) 2023-2024, RV Bionics Group SpA.
 * All rights reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation
 */


#ifndef WDB_AGENTS_WRAPPERS_H
#define WDB_AGENTS_WRAPPERS_H

#include "../securics_db/wdb.h"

cJSON* __wrap_wdb_agents_get_sys_osinfo(wdb_t *wdb);
bool __wrap_wdb_agents_find_package(wdb_t *wdb, const char* reference);
#endif
