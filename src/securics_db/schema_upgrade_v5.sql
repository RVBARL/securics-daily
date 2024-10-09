/*
 * SQL Schema for upgrading databases
 * Copyright (C) 2023-2024, RV Bionics Group SpA.
 *
 * April 23, 2020.
 *
 * This program is a free software, you can redistribute it
 * and/or modify it under the terms of GPLv2.
*/

PRAGMA journal_mode=DELETE;

INSERT OR REPLACE INTO metadata (key, value) VALUES ('db_version', 5);
