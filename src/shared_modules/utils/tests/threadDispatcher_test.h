/*
 * Securics shared modules utils
 * Copyright (C) 2023-2024, RV Bionics Group SpA.
 * July 14, 2020.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation.
 */

#ifndef THREAD_DISPATCHER_TESTS_H
#define THREAD_DISPATCHER_TESTS_H
#include "gtest/gtest.h"
#include "gmock/gmock.h"

class ThreadDispatcherTest : public ::testing::Test
{
    protected:

        ThreadDispatcherTest() = default;
        virtual ~ThreadDispatcherTest() = default;

        void SetUp() override;
        void TearDown() override;
};
#endif //THREAD_DISPATCHER_TESTS_H