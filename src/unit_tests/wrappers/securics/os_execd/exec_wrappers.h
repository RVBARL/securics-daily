/* Copyright (C) 2023-2024, RV Bionics Group SpA.
 * All rights reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation
 */


#ifndef OS_EXEC_WRAPPERS_H
#define OS_EXEC_WRAPPERS_H

int __wrap_ReadExecConfig();

char *__wrap_GetCommandbyName(const char *name, int *timeout);

#endif
