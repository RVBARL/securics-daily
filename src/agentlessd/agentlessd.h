/* Copyright (C) 2023-2024, RV Bionics Group SpA.
 * Copyright (C) 2009 Trend Micro Inc.
 * All rights reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation
 */

#ifndef AGENTLESSD_H
#define AGENTLESSD_H

#include "config/agentlessd-config.h"

#ifndef ARGV0
#define ARGV0 "securics-agentlessd"
#endif

/** Prototypes **/

/* Main monitord */
void Agentlessd(void) __attribute__((noreturn));

// Read config
cJSON *getAgentlessConfig(void);
size_t lessdcom_dispatch(char * command, char ** output);
size_t lessdcom_getconfig(const char * section, char ** output);
void * lessdcom_main(__attribute__((unused)) void * arg);

/* Global variables */
extern agentlessd_config lessdc;

#endif /* AGENTLESSD_H */
