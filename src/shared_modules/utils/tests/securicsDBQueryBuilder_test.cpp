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

#include "securicsDBQueryBuilder_test.hpp"
#include "securicsDBQueryBuilder.hpp"
#include <string>

TEST_F(SecuricsDBQueryBuilderTest, GlobalTest)
{
    std::string message = SecuricsDBQueryBuilder::builder().global().selectAll().fromTable("agent").build();
    EXPECT_EQ(message, "global sql SELECT * FROM agent ");
}

TEST_F(SecuricsDBQueryBuilderTest, AgentTest)
{
    std::string message = SecuricsDBQueryBuilder::builder().agent("0").selectAll().fromTable("sys_programs").build();
    EXPECT_EQ(message, "agent 0 sql SELECT * FROM sys_programs ");
}

TEST_F(SecuricsDBQueryBuilderTest, WhereTest)
{
    std::string message = SecuricsDBQueryBuilder::builder()
                              .agent("0")
                              .selectAll()
                              .fromTable("sys_programs")
                              .whereColumn("name")
                              .equalsTo("bash")
                              .build();
    EXPECT_EQ(message, "agent 0 sql SELECT * FROM sys_programs WHERE name = 'bash' ");
}

TEST_F(SecuricsDBQueryBuilderTest, WhereAndTest)
{
    std::string message = SecuricsDBQueryBuilder::builder()
                              .agent("0")
                              .selectAll()
                              .fromTable("sys_programs")
                              .whereColumn("name")
                              .equalsTo("bash")
                              .andColumn("version")
                              .equalsTo("1")
                              .build();
    EXPECT_EQ(message, "agent 0 sql SELECT * FROM sys_programs WHERE name = 'bash' AND version = '1' ");
}

TEST_F(SecuricsDBQueryBuilderTest, WhereOrTest)
{
    std::string message = SecuricsDBQueryBuilder::builder()
                              .agent("0")
                              .selectAll()
                              .fromTable("sys_programs")
                              .whereColumn("name")
                              .equalsTo("bash")
                              .orColumn("version")
                              .equalsTo("1")
                              .build();
    EXPECT_EQ(message, "agent 0 sql SELECT * FROM sys_programs WHERE name = 'bash' OR version = '1' ");
}

TEST_F(SecuricsDBQueryBuilderTest, WhereIsNullTest)
{
    std::string message = SecuricsDBQueryBuilder::builder()
                              .agent("0")
                              .selectAll()
                              .fromTable("sys_programs")
                              .whereColumn("name")
                              .isNull()
                              .build();
    EXPECT_EQ(message, "agent 0 sql SELECT * FROM sys_programs WHERE name IS NULL ");
}

TEST_F(SecuricsDBQueryBuilderTest, WhereIsNotNullTest)
{
    std::string message = SecuricsDBQueryBuilder::builder()
                              .agent("0")
                              .selectAll()
                              .fromTable("sys_programs")
                              .whereColumn("name")
                              .isNotNull()
                              .build();
    EXPECT_EQ(message, "agent 0 sql SELECT * FROM sys_programs WHERE name IS NOT NULL ");
}

TEST_F(SecuricsDBQueryBuilderTest, InvalidValue)
{
    EXPECT_THROW(SecuricsDBQueryBuilder::builder()
                     .agent("0")
                     .selectAll()
                     .fromTable("sys_programs")
                     .whereColumn("name")
                     .equalsTo("bash'")
                     .build(),
                 std::runtime_error);
}

TEST_F(SecuricsDBQueryBuilderTest, InvalidColumn)
{
    EXPECT_THROW(SecuricsDBQueryBuilder::builder()
                     .agent("0")
                     .selectAll()
                     .fromTable("sys_programs")
                     .whereColumn("name'")
                     .equalsTo("bash")
                     .build(),
                 std::runtime_error);
}

TEST_F(SecuricsDBQueryBuilderTest, InvalidTable)
{
    EXPECT_THROW(SecuricsDBQueryBuilder::builder()
                     .agent("0")
                     .selectAll()
                     .fromTable("sys_programs'")
                     .whereColumn("name")
                     .equalsTo("bash")
                     .build(),
                 std::runtime_error);
}

TEST_F(SecuricsDBQueryBuilderTest, GlobalGetCommand)
{
    std::string message = SecuricsDBQueryBuilder::builder().globalGetCommand("agent-info 1").build();
    EXPECT_EQ(message, "global get-agent-info 1 ");
}

TEST_F(SecuricsDBQueryBuilderTest, GlobalFindCommand)
{
    std::string message = SecuricsDBQueryBuilder::builder().globalFindCommand("agent 1").build();
    EXPECT_EQ(message, "global find-agent 1 ");
}

TEST_F(SecuricsDBQueryBuilderTest, GlobalSelectCommand)
{
    std::string message = SecuricsDBQueryBuilder::builder().globalSelectCommand("agent-name 1").build();
    EXPECT_EQ(message, "global select-agent-name 1 ");
}

TEST_F(SecuricsDBQueryBuilderTest, AgentGetOsInfoCommand)
{
    std::string message = SecuricsDBQueryBuilder::builder().agentGetOsInfoCommand("1").build();
    EXPECT_EQ(message, "agent 1 osinfo get ");
}

TEST_F(SecuricsDBQueryBuilderTest, AgentGetHotfixesCommand)
{
    std::string message = SecuricsDBQueryBuilder::builder().agentGetHotfixesCommand("1").build();
    EXPECT_EQ(message, "agent 1 hotfix get ");
}

TEST_F(SecuricsDBQueryBuilderTest, AgentGetPackagesCommand)
{
    std::string message = SecuricsDBQueryBuilder::builder().agentGetPackagesCommand("1").build();
    EXPECT_EQ(message, "agent 1 package get ");
}
