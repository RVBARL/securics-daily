/* Copyright (C) 2023-2024, RV Bionics Group SpA.
 * Copyright (C) 2009 Trend Micro Inc.
 * All right reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation
 */

#ifndef DBDCONFIG_H
#define DBDCONFIG_H

/* Database config structure */
typedef struct _DBConfig {
    unsigned int db_type;
    unsigned int alert_id;
    unsigned int server_id;
    unsigned int error_count;
    unsigned int maxreconnect;
    unsigned int port;

    char *host;
    char *user;
    char *pass;
    char *db;
    char *sock;

    void *conn;
    OSHash *location_hash;

    char **includes;
} DBConfig;

#define MYSQLDB 0x002
#define POSTGDB 0x004

#endif /* DBDCONFIG_H */
