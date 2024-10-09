/*
 * Securics shared modules utils
 * Copyright (C) 2023-2024, RV Bionics Group SpA.
 * September 27, 2022.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation.
 */

#ifndef _CJSON_SMART_DELETER_HPP
#define _CJSON_SMART_DELETER_HPP

#include "customDeleter.hpp"
#include "cJSON.h"

struct CJsonSmartFree final : CustomDeleter<decltype(&cJSON_free), cJSON_free> {};
struct CJsonSmartDeleter final : CustomDeleter<decltype(&cJSON_Delete), cJSON_Delete> {};

#endif // _CJSON_SMART_DELETER_HPP
