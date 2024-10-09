/* Copyright (C) 2023-2024, RV Bionics Group SpA.
 * All rights reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation
 */


#ifndef WDB_POOL_WRAPPERS_H
#define WDB_POOL_WRAPPERS_H

#include "../securics_db/wdb.h"

wdb_t * __wrap_wdb_pool_get(const char * name);

wdb_t * __wrap_wdb_pool_get_or_create(const char * name);

void __wrap_wdb_pool_leave(__attribute__((unused))wdb_t * node);

char ** __wrap_wdb_pool_keys();

void __wrap_wdb_pool_clean();

#endif
