/* Copyright (C) 2023-2024, RV Bionics Group SpA.
 * All rights reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation
 */


#ifndef SIGNAL_WRAPPERS_H
#define SIGNAL_WRAPPERS_H

#include <signal.h>
#include <sys/types.h>

int __wrap_kill(pid_t pid, int sig);

#endif // SIGNAL_WRAPPERS_H
