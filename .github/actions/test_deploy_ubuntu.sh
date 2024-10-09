#!/bin/bash

# Copyright (C) 2023-2024, RV Bionics Group SpA.
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public
# License (version 2) as published by the FSF - Free Software
# Foundation.

# Global variables
VERSION="$(sed 's/v//' src/VERSION)"
MAJOR=$(echo "${VERSION}" | cut -dv -f2 | cut -d. -f1)
MINOR=$(echo "${VERSION}" | cut -d. -f2)
SHA="$(git rev-parse --short=7 "$1")"

conf_path="/var/ossec/etc/ossec.conf"

VARS=( "SECURICS_MANAGER" "SECURICS_MANAGER_PORT" "SECURICS_PROTOCOL" "SECURICS_REGISTRATION_SERVER" "SECURICS_REGISTRATION_PORT" "SECURICS_REGISTRATION_PASSWORD" "SECURICS_KEEP_ALIVE_INTERVAL" "SECURICS_TIME_RECONNECT" "SECURICS_REGISTRATION_CA" "SECURICS_REGISTRATION_CERTIFICATE" "SECURICS_REGISTRATION_KEY" "SECURICS_AGENT_NAME" "SECURICS_AGENT_GROUP" "ENROLLMENT_DELAY" )
VALUES=( "1.1.1.1" "7777" "udp" "2.2.2.2" "8888" "password" "10" "10" "/var/ossec/etc/testsslmanager.cert" "/var/ossec/etc/testsslmanager.cert" "/var/ossec/etc/testsslmanager.key" "test-agent" "test-group" "10" )
TAGS1=( "<address>" "<port>" "<protocol>" "<manager_address>" "<port>" "<password>" "<notify_time>" "<time-reconnect>" "<server_ca_path>" "<agent_certificate_path>" "<agent_key_path>" "<agent_name>" "<groups>" "<delay_after_enrollment>" )
TAGS2=( "</address>" "</port>" "</protocol>" "</manager_address>" "</port>" "</password>" "</notify_time>" "</time-reconnect>" "</server_ca_path>" "</agent_certificate_path>" "</agent_key_path>" "</agent_name>" "</groups>" "</delay_after_enrollment>" )
SECURICS_REGISTRATION_PASSWORD_PATH="/var/ossec/etc/authd.pass"

function install_securics(){

  echo "Testing the following variables $*"
  eval "${*} apt install -y ./securics-agent_${VERSION}-0.commit${SHA}_amd64.deb > /dev/null 2>&1"
  
}

function remove_securics () {

  apt purge -y securics-agent > /dev/null 2>&1

}

function test() {

  for i in "${!VARS[@]}"; do
    if ( echo "${@}" | grep -q -w "${VARS[i]}" ); then
      if [ "${VARS[i]}" == "SECURICS_MANAGER" ] || [ "${VARS[i]}" == "SECURICS_PROTOCOL" ]; then
        LIST=( "${VALUES[i]//,/ }" )
        for j in "${!LIST[@]}"; do
          if ( grep -q "${TAGS1[i]}${LIST[j]}${TAGS2[i]}" "${conf_path}" ); then
            echo "The variable ${VARS[i]} is set correctly"
          else
            echo "The variable ${VARS[i]} is not set correctly"
            exit 1
          fi
        done
      elif [ "${VARS[i]}" == "SECURICS_REGISTRATION_PASSWORD" ]; then
        if ( grep -q "${VALUES[i]}" "${SECURICS_REGISTRATION_PASSWORD_PATH}" ); then
          echo "The variable ${VARS[i]} is set correctly"
        else
          echo "The variable ${VARS[i]} is not set correctly"
          exit 1
        fi
      else
        if ( grep -q "${TAGS1[i]}${VALUES[i]}${TAGS2[i]}" "${conf_path}" ); then
          echo "The variable ${VARS[i]} is set correctly"
        else
          echo "The variable ${VARS[i]} is not set correctly"
          exit 1
        fi
      fi
    fi
  done

}

echo "Download package: https://s3.us-west-1.amazonaws.com/packages-dev.rvbionics.com/warehouse/pullrequests/${MAJOR}.${MINOR}/deb/var/securics-agent_${VERSION}-0.commit${SHA}_amd64.deb"
wget "https://s3.us-west-1.amazonaws.com/packages-dev.rvbionics.com/warehouse/pullrequests/${MAJOR}.${MINOR}/deb/var/securics-agent_${VERSION}-0.commit${SHA}_amd64.deb" > /dev/null 2>&1

install_securics "SECURICS_MANAGER=1.1.1.1 SECURICS_MANAGER_PORT=7777 SECURICS_PROTOCOL=udp SECURICS_REGISTRATION_SERVER=2.2.2.2 SECURICS_REGISTRATION_PORT=8888 SECURICS_REGISTRATION_PASSWORD=password SECURICS_KEEP_ALIVE_INTERVAL=10 SECURICS_TIME_RECONNECT=10 SECURICS_REGISTRATION_CA=/var/ossec/etc/testsslmanager.cert SECURICS_REGISTRATION_CERTIFICATE=/var/ossec/etc/testsslmanager.cert SECURICS_REGISTRATION_KEY=/var/ossec/etc/testsslmanager.key SECURICS_AGENT_NAME=test-agent SECURICS_AGENT_GROUP=test-group ENROLLMENT_DELAY=10" 
test "SECURICS_MANAGER SECURICS_MANAGER_PORT SECURICS_PROTOCOL SECURICS_REGISTRATION_SERVER SECURICS_REGISTRATION_PORT SECURICS_REGISTRATION_PASSWORD SECURICS_KEEP_ALIVE_INTERVAL SECURICS_TIME_RECONNECT SECURICS_REGISTRATION_CA SECURICS_REGISTRATION_CERTIFICATE SECURICS_REGISTRATION_KEY SECURICS_AGENT_NAME SECURICS_AGENT_GROUP ENROLLMENT_DELAY" 
remove_securics

install_securics "SECURICS_MANAGER=1.1.1.1"
test "SECURICS_MANAGER"
remove_securics

install_securics "SECURICS_MANAGER_PORT=7777"
test "SECURICS_MANAGER_PORT"
remove_securics

install_securics "SECURICS_PROTOCOL=udp"
test "SECURICS_PROTOCOL"
remove_securics

install_securics "SECURICS_REGISTRATION_SERVER=2.2.2.2"
test "SECURICS_REGISTRATION_SERVER"
remove_securics

install_securics "SECURICS_REGISTRATION_PORT=8888"
test "SECURICS_REGISTRATION_PORT"
remove_securics

install_securics "SECURICS_REGISTRATION_PASSWORD=password"
test "SECURICS_REGISTRATION_PASSWORD"
remove_securics

install_securics "SECURICS_KEEP_ALIVE_INTERVAL=10"
test "SECURICS_KEEP_ALIVE_INTERVAL"
remove_securics

install_securics "SECURICS_TIME_RECONNECT=10"
test "SECURICS_TIME_RECONNECT"
remove_securics

install_securics "SECURICS_REGISTRATION_CA=/var/ossec/etc/testsslmanager.cert"
test "SECURICS_REGISTRATION_CA"
remove_securics

install_securics "SECURICS_REGISTRATION_CERTIFICATE=/var/ossec/etc/testsslmanager.cert"
test "SECURICS_REGISTRATION_CERTIFICATE"
remove_securics

install_securics "SECURICS_REGISTRATION_KEY=/var/ossec/etc/testsslmanager.key"
test "SECURICS_REGISTRATION_KEY"
remove_securics

install_securics "SECURICS_AGENT_NAME=test-agent"
test "SECURICS_AGENT_NAME"
remove_securics

install_securics "SECURICS_AGENT_GROUP=test-group"
test "SECURICS_AGENT_GROUP"
remove_securics

install_securics "ENROLLMENT_DELAY=10"
test "ENROLLMENT_DELAY"
remove_securics
