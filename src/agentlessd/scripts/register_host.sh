#!/bin/sh

# Agentless monitoring
#
# Copyright (C) 2023-2024, RV Bionics Group SpA.
# Copyright (C) 2009 Trend Micro Inc.
# All rights reserved.
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public
# License (version 2) as published by the FSF - Free Software
# Foundation.

MYNAME="register_host.sh"
MYPASS=".passlist"

# Check the location
ls -la $MYNAME > /dev/null 2>&1
if [ ! $? = 0 ]; then
    LOCALDIR=`dirname $0`;
    cd ${LOCALDIR}

    ls -la $MYNAME > /dev/null 2>&1
    if [ ! $? = 0 ]; then
        echo "ERROR: You must run this script from the same directory."
        exit 1;
    fi
fi

# Arguments
if [ "x$1" = "x" -o "x$1" = "xhelp" -o "x$1" = "x-h" ]; then
    echo "$0 options:"
    echo "        add <user@host> [<passwd>] (<additional_pass>)"
    echo "        list (passwords)"
    exit 0;
fi

if [ "x$1" = "xlist" ]; then
    echo "*Available hosts: "
    if [ "x$2" = "xpasswords" ]; then
        base64 --decode $MYPASS | sort | uniq;
    else
        base64 --decode $MYPASS | cut -d "|" -f 1 | sort | uniq;
    fi
    exit 0;

elif [ "x$1" = "xadd" ]; then
    if [ "x$2" = "x" ]; then
        echo "ERROR: Missing hostname name.";
        echo "ex: $0 add <user@host> [<passwd>] (<additional_pass>)";
        exit 1;
    fi

    base64 --decode $MYPASS 2> /dev/null | grep "$2|" > /dev/null 2>&1
    if [ $? = 0 ]; then
        echo "ERROR: Host '$2' already added.";
        exit 1;
    fi

    # Check if the password was supplied
    if [ "x$3" = "x" ]; then
        echo "Please provide password for host $2 ('NOPASS' for no password)."
        echo -n "Password: ";
        stty -echo
        read INPASS
        stty echo

        echo "Please provide additional password for host $2 (<enter> for empty)."
        echo -n "Password: ";
        stty -echo
        read ADDPASS
        stty echo
    else
        INPASS=$3
        ADDPASS=$4
    fi

    if [ -f $MYPASS ]; then
        base64 --decode $MYPASS > $MYPASS.tmp && echo "$2|$INPASS|$ADDPASS" >> $MYPASS.tmp && base64 $MYPASS.tmp > $MYPASS
        rm -f $MYPASS.tmp
    else
        echo "$2|$INPASS|$ADDPASS" | base64 - > $MYPASS
    fi

    if [ ! $? = 0 ]; then
        echo "ERROR: Unable to creating entry (echo failed)."
        exit 1;
    fi
    chmod 644 $MYPASS
    echo "*Host $2 added."

else
    echo "ERROR: Invalid argument.";
    exit 1;

fi

