/* Copyright (C) 2023-2024, RV Bionics Group SpA.
 * Copyright (C) 2009 Trend Micro Inc.
 * All right reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation
*/

#include "os_regex.h"
#include "os_regex_internal.h"


int OS_StrStartsWith(const char *str, const char *pattern)
{
    while (*pattern) {
        if (*pattern++ != *str++) {
            return FALSE;
        }
    }

    return TRUE;
}
