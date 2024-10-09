/* Copyright (C) 2023-2024, RV Bionics Group SpA.
 * All rights reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation
 */


#include <stddef.h>
#include <stdarg.h>
#include <setjmp.h>
#include <cmocka.h>
#include "request_wrappers.h"

int __wrap_req_save(const char * counter, const char * buffer, size_t length) {
    check_expected(counter);
    check_expected(buffer);
    check_expected(length);
    return mock();
}
