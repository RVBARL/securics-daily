#! /bin/bash
# By Spransy, Derek" <DSPRANS () emory ! edu> and Charlie Scott
# Modified by Securics, Inc. <info@rvbionics.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv2

#####
# This checks for an error and exits with a custom message
# Returns zero on success
# $1 is the message
# $2 is the error code

DIR="/Library/Ossec"

if [ -d "${DIR}" ]; then
    echo "A Securics agent installation was found in ${DIR}. Will perform an upgrade."

    if [ -f "${DIR}/SECURICS_PKG_UPGRADE" ]; then
        rm -f "${DIR}/SECURICS_PKG_UPGRADE"
    fi
    if [ -f "${DIR}/SECURICS_RESTART" ]; then
        rm -f "${DIR}/SECURICS_RESTART"
    fi

    touch "${DIR}/SECURICS_PKG_UPGRADE"
    upgrade="true"

    if ${DIR}/bin/securics-control status | grep "is running" > /dev/null 2>&1; then
        touch "${DIR}/SECURICS_RESTART"
        restart="true"
    elif ${DIR}/bin/ossec-control status | grep "is running" > /dev/null 2>&1; then
        touch "${DIR}/SECURICS_RESTART"
        restart="true"
    fi
fi

# Stops the agent before upgrading it
echo "Stopping the agent before upgrading it."

if [ -f ${DIR}/bin/securics-control ]; then
    ${DIR}/bin/securics-control stop
elif [ -f ${DIR}/bin/ossec-control ]; then
    ${DIR}/bin/ossec-control stop
fi

if [ -n "${upgrade}" ]; then
    echo "Backing up configuration files to ${DIR}/config_files/"
    mkdir -p ${DIR}/config_files/
    cp -r ${DIR}/etc/{ossec.conf,client.keys,local_internal_options.conf,shared} ${DIR}/config_files/

    if [ -d ${DIR}/logs/ossec ]; then
        echo "Renaming ${DIR}/logs/ossec to ${DIR}/logs/securics"
        mv ${DIR}/logs/ossec ${DIR}/logs/securics
    fi

    if [ -d ${DIR}/queue/ossec ]; then
        echo "Renaming ${DIR}/queue/ossec to ${DIR}/queue/sockets"
        mv ${DIR}/queue/ossec ${DIR}/queue/sockets
    fi
fi

if [ -n "${upgrade}" ]; then
    if pkgutil --pkgs | grep -i securics-agent-etc > /dev/null 2>&1 ; then
        echo "Removing previous package receipt for securics-agent-etc"
        pkgutil --forget com.securics.pkg.securics-agent-etc
    fi
fi

if [[ ! -f "/usr/bin/dscl" ]]
    then
    echo "Error: I couldn't find dscl, dying here";
    exit
fi

DSCL="/usr/bin/dscl";

function check_errm
{
    if  [[ ${?} != "0" ]]
        then
        echo "${1}";
        exit ${2};
        fi
}

# get unique id numbers (uid, gid) that are greater than 100
echo "Getting unique id numbers (uid, gid)"
unset -v i new_uid new_gid idvar;
declare -i new_uid=0 new_gid=0 i=100 idvar=0;
while [[ $idvar -eq 0 ]]; do
    i=$[i+1]
    if [[ -z "$(/usr/bin/dscl . -search /Users uid ${i})" ]] && [[ -z "$(/usr/bin/dscl . -search /Groups gid ${i})" ]];
        then
        echo "Found available UID and GID: $i"
        new_uid=$i
        new_gid=$i
        idvar=1
        #break
   fi
done

echo "UID available for securics user is:";
echo ${new_uid}

# Verify that the uid and gid exist and match
if [[ $new_uid -eq 0 ]] || [[ $new_gid -eq 0 ]];
    then
    echo "Getting unique id numbers (uid, gid) failed!";
    exit 1;
fi
if [[ ${new_uid} != ${new_gid} ]]
    then
    echo "I failed to find matching free uid and gid!";
    exit 5;
fi

# Stops the agent before upgrading it
if [ -f ${DIR}/bin/securics-control ]; then
    ${DIR}/bin/securics-control stop
elif [ -f ${DIR}/bin/ossec-control ]; then
    ${DIR}/bin/ossec-control stop
fi

# Creating the group
echo "Checking group..."
if [[ $(dscl . -read /Groups/securics) ]]
    then
    echo "securics group already exists.";
else
    sudo ${DSCL} localhost -create /Local/Default/Groups/securics
    check_errm "Error creating group securics" "67"
    sudo ${DSCL} localhost -createprop /Local/Default/Groups/securics PrimaryGroupID ${new_gid}
    sudo ${DSCL} localhost -createprop /Local/Default/Groups/securics RealName securics
    sudo ${DSCL} localhost -createprop /Local/Default/Groups/securics RecordName securics
    sudo ${DSCL} localhost -createprop /Local/Default/Groups/securics RecordType: dsRecTypeStandard:Groups
    sudo ${DSCL} localhost -createprop /Local/Default/Groups/securics Password "*"
fi

# Creating the user
echo "Checking user..."
if [[ $(dscl . -read /Users/securics) ]]
    then
    echo "securics user already exists.";
else
    sudo ${DSCL} localhost -create /Local/Default/Users/securics
    check_errm "Error creating user securics" "77"
    sudo ${DSCL} localhost -createprop /Local/Default/Users/securics RecordName securics
    sudo ${DSCL} localhost -createprop /Local/Default/Users/securics RealName securics
    sudo ${DSCL} localhost -createprop /Local/Default/Users/securics UserShell /usr/bin/false
    sudo ${DSCL} localhost -createprop /Local/Default/Users/securics NFSHomeDirectory /var/securics
    sudo ${DSCL} localhost -createprop /Local/Default/Users/securics UniqueID ${new_uid}
    sudo ${DSCL} localhost -createprop /Local/Default/Users/securics PrimaryGroupID ${new_gid}
    sudo ${DSCL} localhost -append /Local/Default/Groups/securics GroupMembership securics
    sudo ${DSCL} localhost -createprop /Local/Default/Users/securics Password "*"
fi

#Hide the fixed users
echo "Hiding the fixed securics user"
dscl . create /Users/securics IsHidden 1