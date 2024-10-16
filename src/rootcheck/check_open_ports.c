/* Copyright (C) 2023-2024, RV Bionics Group SpA.
 * Copyright (C) 2009 Trend Micro Inc.
 * All right reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation
*/

#include "shared.h"
#include "headers/debug_op.h"
#include "headers/defs.h"
#include "rootcheck.h"

#ifndef OSSECHIDS

/* Prototypes */
static int  connect_to_port(int proto, int port);
static void try_to_access_ports(void);

/* Global variables */
static int  _ports_open;
static int  open_ports_size;
static char open_ports_str[OS_SIZE_1024 + 1];


static int connect_to_port(int proto, int port)
{
    int rc = 0;
    int ossock;
    struct sockaddr_in server;

    if (proto == IPPROTO_UDP) {
        if ((ossock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) < 0) {
            return (0);
        }
    } else if (proto == IPPROTO_TCP) {
        if ((ossock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)) < 0) {
            return (0);
        }
    } else {
        return (0);
    }

    memset(&server, 0, sizeof(server));
    server.sin_family      = AF_INET;
    server.sin_port        = htons(port);
    server.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

    if (connect(ossock, (struct sockaddr *)&server, sizeof(server)) == 0) {
        rc = 1;
    }

    close(ossock);

    return (rc);
}

static void try_to_access_ports()
{
    int i;

    for (i = 0; i <= 65535; i++) {
        if (total_ports_tcp[i] && connect_to_port(IPPROTO_TCP, i)) {
            char port_proto[64];

            if (_ports_open == 0) {
                snprintf(port_proto, 64, "\n      %d (tcp),", i);
            } else {
                snprintf(port_proto, 64, "%d (tcp),", i);
            }
            strncat(open_ports_str, port_proto, open_ports_size);
            open_ports_size -= strlen(port_proto) + 1;

            _ports_open++;
        }

        if (total_ports_udp[i] && connect_to_port(IPPROTO_UDP, i)) {
            char port_proto[64];

            if (_ports_open == 0) {
                snprintf(port_proto, 64, "\n      %d (udp),", i);
            } else {
                snprintf(port_proto, 64, "%d (udp),", i);
            }

            strncat(open_ports_str, port_proto, open_ports_size);
            open_ports_size -= strlen(port_proto) + 1;

            _ports_open++;
        }

        if (_ports_open >= 4) {
            _ports_open = 0;
        }
    }

}
#endif

void check_open_ports()
{
#ifndef OSSECHIDS
    memset(open_ports_str, '\0', OS_SIZE_1024 + 1);
    open_ports_size = OS_SIZE_1024 - 1;
    _ports_open = 0;

    snprintf(open_ports_str, OS_SIZE_1024, "The following ports are open:");
    open_ports_size -= strlen(open_ports_str) + 1;

    /* Testing All ports */
    try_to_access_ports();

    open_ports_str[strlen(open_ports_str) - 1] = '\0';

    notify_rk(ALERT_OK, open_ports_str);

#endif
    return;
}

