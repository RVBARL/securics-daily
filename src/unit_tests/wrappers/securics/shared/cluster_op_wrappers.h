/* Copyright (C) 2023-2024, RV Bionics Group SpA.
 * All rights reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation
 */


#ifndef CLUSTER_OP_WRAPPERS_H
#define CLUSTER_OP_WRAPPERS_H

int __wrap_w_is_worker(void);

int __wrap_w_is_single_node(int* is_worker);

#endif
