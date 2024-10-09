/* Copyright (C) 2023-2024, RV Bionics Group SpA.
 * All rights reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation
 */


#ifndef WINSOCK_WRAPPERS_H
#define WINSOCK_WRAPPERS_H

#include <winsock.h>
#define gethostname wrap_gethostname

int wrap_gethostname(char *name, int len);

#endif
