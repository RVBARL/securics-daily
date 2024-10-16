/* Copyright (C) 2023-2024, RV Bionics Group SpA.
 * Copyright (C) 2009 Trend Micro Inc.
 * All rights reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation.
 */

#include "../plugin_decoders.h"

#include "shared.h"
#include "eventinfo.h"

/* Regex to extract the priority and event id */
#define SONICWALL_REGID  "pri=(\\d) c=(\\d+) m=(\\d+) "

/* Regex to extract the srcip and dst ip */
#define SONICWALL_REGEX "src=(\\d+.\\d+.\\d+.\\d+):(\\d+):\\S+ " \
                        "dst=(\\d+.\\d+.\\d+.\\d+):(\\d+):"

/* Regex for the web proxy messages */
#define SONICWALL_PROXY "result=(\\d+) dstname=(\\S+) arg=(\\S+)$"

/* Global variables -- not thread safe. If we ever multi thread
 * analysisd, these will need to be changed.
 */
static OSRegex *__sonic_regex_prid = NULL;
static OSRegex *__sonic_regex_sdip = NULL;
static OSRegex *__sonic_regex_prox = NULL;
static bool __sonic_plugin_initialized = false;


void *SonicWall_Decoder_Init()
{
    if (__sonic_plugin_initialized) {
        return NULL;
    }

    mdebug1("Initializing SonicWall decoder..");

    /* Allocate memory */
    os_calloc(1, sizeof(OSRegex), __sonic_regex_sdip);
    os_calloc(1, sizeof(OSRegex), __sonic_regex_prid);
    os_calloc(1, sizeof(OSRegex), __sonic_regex_prox);

    /* Compile our regexes */
    if (!OSRegex_Compile(SONICWALL_REGEX, __sonic_regex_sdip, OS_RETURN_SUBSTRING)) {
        merror(REGEX_COMPILE, SONICWALL_REGEX, __sonic_regex_sdip->error);
        return (0);
    }
    if (!OSRegex_Compile(SONICWALL_REGID, __sonic_regex_prid, OS_RETURN_SUBSTRING)) {
        merror(REGEX_COMPILE, SONICWALL_REGID, __sonic_regex_prid->error);
        return (0);
    }
    if (!OSRegex_Compile(SONICWALL_PROXY, __sonic_regex_prox, OS_RETURN_SUBSTRING)) {
        merror(REGEX_COMPILE, SONICWALL_PROXY, __sonic_regex_prox->error);
        return (0);
    }

    /* We must have the sub_strings to retrieve the nodes */
    if (!__sonic_regex_sdip->d_sub_strings) {
        merror(REGEX_SUBS, SONICWALL_REGEX);
        return (0);
    }
    if (!__sonic_regex_prid->d_sub_strings) {
        merror(REGEX_SUBS, SONICWALL_REGID);
        return (0);
    }
    if (!__sonic_regex_prox->d_sub_strings) {
        merror(REGEX_SUBS, SONICWALL_PROXY);
        return (0);
    }

    /* There is nothing else to do over here */
    __sonic_plugin_initialized = true;
    return (NULL);
}

/* SonicWall decoder
 * Will extract the id, severity, action, srcip, dstip, protocol,srcport,dstport
 * severity will be extracted as status.
 * Examples:
 * Jan  3 13:45:36 192.168.5.1 id=firewall sn=000SERIAL time="2007-01-03 14:48:06" fw=1.1.1.1 pri=6 c=262144 m=98 msg="Connection Opened" n=23419 src=2.2.2.2:36701:WAN dst=1.1.1.1:50000:WAN proto=tcp/50000
 * Jan  3 13:45:36 192.168.5.1 id=firewall sn=000SERIAL time="2007-01-03 14:48:07" fw=1.1.1.1 pri=1 c=32 m=30 msg="Administrator login denied due to bad credentials" n=7 src=2.2.2.2:36701:WAN dst=1.1.1.1:50000:WAN
 */
void *SonicWall_Decoder_Exec(Eventinfo *lf, regex_matching *decoder_match)
{
    int i = 0;
    char category[8];
    const char *tmp_str = NULL;

    /* Zero category */
    category[0] = '\0';
    lf->decoder_info->type = SYSLOG;

    /* First run regex to extract the severity, cat and id */
    if (!(tmp_str = OSRegex_Execute_ex(lf->log, __sonic_regex_prid, decoder_match))) {
        return (NULL);
    }

    /* Get severity, id and category */
    if (decoder_match->sub_strings[0] &&
            decoder_match->sub_strings[1] &&
            decoder_match->sub_strings[2]) {
        lf->status = decoder_match->sub_strings[0];
        lf->id = decoder_match->sub_strings[2];

        /* Get category */
        strncpy(category, decoder_match->sub_strings[1], 7);

        /* Clear all substrings */
        decoder_match->sub_strings[0] = NULL;
        decoder_match->sub_strings[2] = NULL;

        free(decoder_match->sub_strings[1]);
        decoder_match->sub_strings[1] = NULL;
    } else {
        i = 0;
        while (decoder_match->sub_strings[i]) {
            free(decoder_match->sub_strings[i]);
            decoder_match->sub_strings[i] = NULL;
            i++;
        }

        return (NULL);
    }

    /* Get ips and ports */
    if (!(tmp_str = OSRegex_Execute_ex(tmp_str, __sonic_regex_sdip, decoder_match))) {
        return (NULL);
    }
    if (decoder_match->sub_strings[0] &&
            decoder_match->sub_strings[1] &&
            decoder_match->sub_strings[2] &&
            decoder_match->sub_strings[3]) {
        /* Set all the values */
        lf->srcip = decoder_match->sub_strings[0];
        lf->srcport = decoder_match->sub_strings[1];
        lf->dstip = decoder_match->sub_strings[2];
        lf->dstport = decoder_match->sub_strings[3];

        /* Clear substrings */
        decoder_match->sub_strings[0] = NULL;
        decoder_match->sub_strings[1] = NULL;
        decoder_match->sub_strings[2] = NULL;
        decoder_match->sub_strings[3] = NULL;

        /* Look for protocol */
        tmp_str = strchr(tmp_str, ' ');
        if (tmp_str) {
            tmp_str++;
            if (strncmp(tmp_str, "proto=", 6) == 0) {
                char *proto = NULL;

                i = 0;
                tmp_str += 6;

                /* Allocate memory for the protocol */
                os_calloc(8, sizeof(char), proto);
                while (isValidChar(*tmp_str) && (*tmp_str != '/')) {
                    proto[i] = *tmp_str;
                    i++;
                    tmp_str++;

                    if (i >= 6) {
                        break;
                    }
                }

                /* Set protocol to event info structure */
                lf->protocol = proto;
            }
        }
    } else {
        i = 0;
        while (decoder_match->sub_strings[i]) {
            free(decoder_match->sub_strings[i]);
            decoder_match->sub_strings[i] = 0;
            i++;
        }

        return (NULL);
    }

    /* Set the category/action based on the id */

    /* IDS event */
    if (strcmp(category, "32") == 0) {
        lf->decoder_info->type = IDS;
    }

    /* Firewall connection opened */
    else if ((strcmp(lf->id, "98") == 0) ||
             (strcmp(lf->id, "597") == 0) ||
             (strcmp(lf->id, "598") == 0)) {
        lf->decoder_info->type = FIREWALL;
        os_strdup("pass", lf->action);
    }

    /* Firewall connection dropped */
    else if ((strcmp(lf->id, "38") == 0) ||
             (strcmp(lf->id, "36") == 0) ||
             (strcmp(lf->id, "173") == 0) ||
             (strcmp(lf->id, "174") == 0) ||
             (strcmp(lf->id, "37") == 0)) {
        lf->decoder_info->type = FIREWALL;
        os_strdup("drop", lf->action);
    }

    /* Firewall connection closed */
    else if (strcmp(lf->id, "537") == 0) {
        lf->decoder_info->type = FIREWALL;
        os_strdup("close", lf->action);
    }

    /* Proxy msg */
    else if (strcmp(lf->id, "97") == 0) {
        lf->decoder_info->type = SQUID;

        /* Check if tmp_str is valid */
        if (!tmp_str) {
            return (NULL);
        }

        /* First run regex to extract the severity and id */
        if (!OSRegex_Execute_ex(tmp_str, __sonic_regex_prox, decoder_match)) {
            return (NULL);
        }

        /* Get HTTP responde code as id */
        if (decoder_match->sub_strings[0]) {
            free(lf->id);
            lf->id = decoder_match->sub_strings[0];
            decoder_match->sub_strings[0] = NULL;
        } else {
            return (NULL);
        }

        /* Get HTTP page */
        if (decoder_match->sub_strings[1] &&
                decoder_match->sub_strings[2]) {
            char *final_url;
            size_t url_size = strlen(decoder_match->sub_strings[1]) +
                           strlen(decoder_match->sub_strings[2]) + 2;

            os_calloc(url_size + 1, sizeof(char), final_url);
            snprintf(final_url, url_size, "%s%s",
                     decoder_match->sub_strings[1],
                     decoder_match->sub_strings[2]);


            /* Clear memory */
            free(decoder_match->sub_strings[1]);
            free(decoder_match->sub_strings[2]);
            decoder_match->sub_strings[1] = NULL;
            decoder_match->sub_strings[2] = NULL;

            /* Set the URL */
            lf->url = final_url;
        } else {
            merror("Error getting regex - SonicWall." );
        }

        return (NULL);
    }

    return (NULL);
}
