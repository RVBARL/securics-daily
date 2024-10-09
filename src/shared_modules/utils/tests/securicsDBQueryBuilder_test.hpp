/*
 * Securics shared modules utils
 * Copyright (C) 2023-2024, RV Bionics Group SpA.
 * Nov 1, 2023.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation.
 */

#ifndef _SECURICS_DB_QUERY_BUILDER_TEST_HPP
#define _SECURICS_DB_QUERY_BUILDER_TEST_HPP

#include "gtest/gtest.h"

class SecuricsDBQueryBuilderTest : public ::testing::Test
{
protected:
    SecuricsDBQueryBuilderTest() = default;
    virtual ~SecuricsDBQueryBuilderTest() = default;

    void SetUp() override {};
    void TearDown() override {};
};

#endif // _SECURICS_DB_QUERY_BUILDER_TEST_HPP
