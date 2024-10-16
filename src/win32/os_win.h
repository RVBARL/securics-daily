/* Copyright (C) 2023-2024, RV Bionics Group SpA.
 * Copyright (C) 2009 Trend Micro Inc.
 * All rights reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation
 */

#ifndef OS_WIN_H
#define OS_WIN_H

/* Install the SECURICS-HIDS agent service */
int InstallService(char *path);

/* Uninstall the SECURICS-HIDS agent service */
int UninstallService();

/* Check if the SECURICS-HIDS agent service is running
 * Returns 1 on success (running) or 0 if not running
 */
int CheckServiceRunning();

/* Start SECURICS-HIDS service */
int os_start_service();

/* Stop SECURICS-HIDS service */
int os_stop_service();

/* Start the process from the services */
int os_WinMain(int argc, char **argv);

/* Locally start the process (after the services initialization) */
int local_start();

#endif /* OS_WIN_H */
