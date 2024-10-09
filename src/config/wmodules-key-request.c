/* Copyright (C) 2023-2024, RV Bionics Group SpA.
 * All right reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation
*/

#include "securics_modules/wmodules.h"
#include <stdio.h>

// Reading function
int wm_key_request_read(__attribute__((unused)) xml_node **nodes, __attribute__((unused)) void *module) {
    minfo("Ignoring configuration block for deprecated agent-key-polling module: This configuration is read now by Authd.");
    return 0;
}
