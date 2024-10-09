<!---
Copyright (C) 2023-2024, RV Bionics Group SpA.
Created by Securics, Inc. <info@rvbionics.com>.
This program is free software; you can redistribute it and/or modify it under the terms of GPLv2
-->

# Centralized Configuration
## Index
- [Centralized Configuration](#centralized-configuration)
  - [Index](#index)
  - [Purpose](#purpose)
  - [Sequence diagram](#sequence-diagram)

## Purpose

One of the key features of Securics as a EDR is the Centralized Configuration, allowing to deploy configurations, policies, rootcheck descriptions or any other file from Securics Manager to any Securics Agent based on their grouping configuration. This feature has multiples actors: Securics Cluster (Master and Worker nodes), with `securics-remoted` as the main responsible from the managment side, and Securics Agent with `securics-agentd` as resposible from the client side.


## Sequence diagram
Sequence diagram shows the basic flow of Centralized Configuration based on the configuration provided. There are mainly three stages:
1. Securics Manager Master Node (`securics-remoted`) creates every `remoted.shared_reload` (internal) seconds the files that need to be synchronized with the agents.
2. Securics Cluster as a whole (via `securics-clusterd`) continuously synchronize files between Securics Manager Master Node and Securics Manager Worker Nodes
3. Securics Agent `securics-agentd` (via ) sends every `notify_time` (ossec.conf) their status, being `merged.mg` hash part of it. Securics Manager Worker Node (`securics-remoted`) will check if agent's `merged.mg` is out-of-date, and in case this is true, the new `merged.mg` will be pushed to Securics Agent.