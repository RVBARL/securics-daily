/* Copyright (C) 2023-2024, RV Bionics Group SpA.
 * All rights reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation
 */


#include <openssl/evp.h>

EVP_PKEY * __wrap_EVP_PKEY_new(void);
extern EVP_PKEY * __real_EVP_PKEY_new(void);
