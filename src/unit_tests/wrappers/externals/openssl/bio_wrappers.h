/* Copyright (C) 2023-2024, RV Bionics Group SpA.
 * All rights reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation
 */


#ifndef BIO_WRAPPERS_H
#define BIO_WRAPPERS_H

#include <openssl/ssl.h>

BIO *__wrap_BIO_new_socket(int sock, int close_flag);

#endif
