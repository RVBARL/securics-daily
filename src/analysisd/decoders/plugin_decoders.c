/* Copyright (C) 2023-2024, RV Bionics Group SpA.
 * Copyright (C) 2015 Trend Micro Inc.
 * All rights reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation.
 */

#include "plugin_decoders.h"

/* List of plugins. All three lists must be in the same order */
const char *(plugin_decoders[]) = {"PF_Decoder",
                             "SymantecWS_Decoder",
                             "SonicWall_Decoder",
                             "OSSECAlert_Decoder",
                             "JSON_Decoder",
                             NULL
                            };
void *(plugin_decoders_init[]) = {PF_Decoder_Init,
                                  SymantecWS_Decoder_Init,
                                  SonicWall_Decoder_Init,
                                  OSSECAlert_Decoder_Init,
                                  JSON_Decoder_Init,
                                  NULL
                                 };
void *(plugin_decoders_exec[]) = {PF_Decoder_Exec,
                                  SymantecWS_Decoder_Exec,
                                  SonicWall_Decoder_Exec,
                                  OSSECAlert_Decoder_Exec,
                                  JSON_Decoder_Exec,
                                  NULL
                                 };
