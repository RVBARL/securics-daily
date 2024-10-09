/* Copyright (C) 2023-2024, RV Bionics Group SpA.
 * All rights reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation
 */


#ifndef REMOTED_OP_WRAPPERS_H
#define REMOTED_OP_WRAPPERS_H

#include "../../../../securics_db/wdb.h"

int __wrap_parse_agent_update_msg(char *msg, __attribute__((unused)) agent_info_data *agent_data);

#endif
