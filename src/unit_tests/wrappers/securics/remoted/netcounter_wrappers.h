/* Copyright (C) 2023-2024, RV Bionics Group SpA.
 * All rights reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation
 */

#ifndef NETCOUNTER_WRAPPERS_H
#define NETCOUNTER_WRAPPERS_H

void __wrap_rem_setCounter(int fd, size_t counter);
size_t __wrap_rem_getCounter(int fd);

#endif
