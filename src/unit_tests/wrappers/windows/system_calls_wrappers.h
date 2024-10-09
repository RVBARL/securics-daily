/* Copyright (C) 2023-2024, RV Bionics Group SpA.
 * All rights reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation
 */

#ifndef SYSTEM_CALLS_WRAPPERS_H
#define SYSTEM_CALLS_WRAPPERS_H

//#undef _mktemp_s
//#define _mktemp_s  wrap_mktemp_s

char * wrap_getenv(const char *name);

#endif
