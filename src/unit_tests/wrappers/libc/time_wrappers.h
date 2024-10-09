/* Copyright (C) 2023-2024, RV Bionics Group SpA.
 * All rights reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation
 */


#ifndef TIME_WRAPPERS_H
#define TIME_WRAPPERS_H

#include <time.h>

size_t __wrap_strftime(char *s, size_t max, const char *format, const struct tm *tm);
#endif
