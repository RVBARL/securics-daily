<!---
Copyright (C) 2023-2024, RV Bionics Group SpA.
Created by Securics, Inc. <info@rvbionics.com>.
This program is free software; you can redistribute it and/or modify it under the terms of GPLv2
-->

# Metrics

## Index

- [Metrics](#metrics)
  - [Index](#index)
  - [Purpose](#purpose)
  - [Sequence diagram](#sequence-diagram)

## Purpose

Securics includes some metrics to understand the behavior of its components, which allow to investigate errors and detect problems with some configurations. This feature has multiple actors: `securics-remoted` for agent interaction messages, `securics-analysisd` for processed events.

## Sequence diagram

The sequence diagram shows the basic flow of metric counters. These are the main flows:

1. Messages received by `securics-remoted` from agents.
2. Messages that `securics-remoted` sends to agents.
3. Events received by `securics-analysisd`.
4. Events processed by `securics-analysisd`.
