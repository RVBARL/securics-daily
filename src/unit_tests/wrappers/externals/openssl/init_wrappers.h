/* Copyright (C) 2023-2024, RV Bionics Group SpA.
 * All rights reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation
 */


#ifndef INIT_WRAPPERS_H
#define INIT_WRAPPERS_H

#include <stdint.h>
#include <openssl/crypto.h>

int __wrap_OPENSSL_init_crypto(uint64_t opts,
                               const OPENSSL_INIT_SETTINGS *settings);

#endif
