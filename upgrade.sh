#!/bin/bash
# Copyright (C) 2023-2024, RV Bionics Group SpA.

# validate OS, linux or macos
if [ "X$(uname)" = "XLinux" ] ; then
    # Get Securics installation path
    SCRIPT=$(readlink -f "$0")
    SECURICS_HOME=$(dirname $(dirname $(dirname "$SCRIPT")))
    cd "${SECURICS_HOME}"
    (sleep 5 && chmod +x ./var/upgrade/*.sh && ./var/upgrade/pkg_installer.sh && find ./var/upgrade/* -not -name upgrade_result -delete) >/dev/null 2>&1 &
else
    (sleep 5 && chmod +x ./var/upgrade/*.sh && ./var/upgrade/pkg_installer.sh && find ./var/upgrade/ -mindepth 1 -not -name upgrade_result -delete) >/dev/null 2>&1 &
fi
