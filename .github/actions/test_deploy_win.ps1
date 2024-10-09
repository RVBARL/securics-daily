# Copyright (C) 2023-2024, RV Bionics Group SpA.
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public
# License (version 2) as published by the FSF - Free Software
# Foundation.

$VERSION = Get-Content src/VERSION
[version]$VERSION = $VERSION -replace '[v]',''
$MAJOR=$VERSION.Major
$MINOR=$VERSION.Minor
$SHA= git rev-parse --short $args[0]

$TEST_ARRAY=@( 
              @("SECURICS_MANAGER ", "1.1.1.1", "<address>", "</address>"), 
              @("SECURICS_MANAGER_PORT ", "7777", "<port>", "</port>"),
              @("SECURICS_PROTOCOL ", "udp", "<protocol>", "</protocol>"),
              @("SECURICS_REGISTRATION_SERVER ", "2.2.2.2", "<manager_address>", "</manager_address>"),
              @("SECURICS_REGISTRATION_PORT ", "8888", "<port>", "</port>"),
              @("SECURICS_REGISTRATION_PASSWORD ", "password", "<password>", "</password>"),
              @("SECURICS_KEEP_ALIVE_INTERVAL ", "10", "<notify_time>", "</notify_time>"),
              @("SECURICS_TIME_RECONNECT ", "10", "<time-reconnect>", "</time-reconnect>"),
              @("SECURICS_REGISTRATION_CA ", "/var/ossec/etc/testsslmanager.cert", "<server_ca_path>", "</server_ca_path>"),
              @("SECURICS_REGISTRATION_CERTIFICATE ", "/var/ossec/etc/testsslmanager.cert", "<agent_certificate_path>", "</agent_certificate_path>"),
              @("SECURICS_REGISTRATION_KEY ", "/var/ossec/etc/testsslmanager.key", "<agent_key_path>", "</agent_key_path>"),
              @("SECURICS_AGENT_NAME ", "test-agent", "<agent_name>", "</agent_name>"),
              @("SECURICS_AGENT_GROUP ", "test-group", "<groups>", "</groups>"),
              @("ENROLLMENT_DELAY ", "10", "<delay_after_enrollment>", "</delay_after_enrollment>")
)

function install_securics($vars)
{

    Write-Output "Testing the following variables $vars"
    Start-Process  C:\Windows\System32\msiexec.exe -ArgumentList  "/i securics-agent-$VERSION-0.commit$SHA.msi /qn $vars" -wait
    
}

function remove_securics
{

    Start-Process  C:\Windows\System32\msiexec.exe -ArgumentList "/x securics-agent-$VERSION-commit$SHA.msi /qn" -wait

}

function test($vars)
{

  For ($i=0; $i -lt $TEST_ARRAY.Length; $i++) {
    if($vars.Contains($TEST_ARRAY[$i][0])) {
      if ( ($TEST_ARRAY[$i][0] -eq "SECURICS_MANAGER ") -OR ($TEST_ARRAY[$i][0] -eq "SECURICS_PROTOCOL ") ) {
        $LIST = $TEST_ARRAY[$i][1].split(",")
        For ($j=0; $j -lt $LIST.Length; $j++) {
          $SEL = Select-String -Path 'C:\Program Files (x86)\ossec-agent\ossec.conf' -Pattern "$($TEST_ARRAY[$i][2])$($LIST[$j])$($TEST_ARRAY[$i][3])"
          if($SEL -ne $null) {
            Write-Output "The variable $($TEST_ARRAY[$i][0]) is set correctly"
          }
          if($SEL -eq $null) {
            Write-Output "The variable $($TEST_ARRAY[$i][0]) is not set correctly"
            exit 1
          }
        }
      }
      ElseIf ( ($TEST_ARRAY[$i][0] -eq "SECURICS_REGISTRATION_PASSWORD ") ) {
        if (Test-Path 'C:\Program Files (x86)\ossec-agent\authd.pass'){
          $SEL = Select-String -Path 'C:\Program Files (x86)\ossec-agent\authd.pass' -Pattern "$($TEST_ARRAY[$i][1])"
          if($SEL -ne $null) {
            Write-Output "The variable $($TEST_ARRAY[$i][0]) is set correctly"
          }
          if($SEL -eq $null) {
            Write-Output "The variable $($TEST_ARRAY[$i][0]) is not set correctly"
            exit 1
          }
        }
        else
        {
          Write-Output "SECURICS_REGISTRATION_PASSWORD is not correct"
          exit 1
        }
      }
      Else {
        $SEL = Select-String -Path 'C:\Program Files (x86)\ossec-agent\ossec.conf' -Pattern "$($TEST_ARRAY[$i][2])$($TEST_ARRAY[$i][1])$($TEST_ARRAY[$i][3])"
        if($SEL -ne $null) {
          Write-Output "The variable $($TEST_ARRAY[$i][0]) is set correctly"
        }
        if($SEL -eq $null) {
          Write-Output "The variable $($TEST_ARRAY[$i][0]) is not set correctly"
          exit 1
        }
      }
    }
  }

}

Write-Output "Download package: https://s3.us-west-1.amazonaws.com/packages-dev.rvbionics.com/warehouse/pullrequests/$MAJOR.$MINOR/windows/securics-agent-$VERSION-0.commit$SHA.msi"
Invoke-WebRequest -Uri "https://s3.us-west-1.amazonaws.com/packages-dev.rvbionics.com/warehouse/pullrequests/$MAJOR.$MINOR/windows/securics-agent-$VERSION-0.commit$SHA.msi" -OutFile "securics-agent-$VERSION-0.commit$SHA.msi"

install_securics "SECURICS_MANAGER=1.1.1.1 SECURICS_MANAGER_PORT=7777 SECURICS_PROTOCOL=udp SECURICS_REGISTRATION_SERVER=2.2.2.2 SECURICS_REGISTRATION_PORT=8888 SECURICS_REGISTRATION_PASSWORD=password SECURICS_KEEP_ALIVE_INTERVAL=10 SECURICS_TIME_RECONNECT=10 SECURICS_REGISTRATION_CA=/var/ossec/etc/testsslmanager.cert SECURICS_REGISTRATION_CERTIFICATE=/var/ossec/etc/testsslmanager.cert SECURICS_REGISTRATION_KEY=/var/ossec/etc/testsslmanager.key SECURICS_AGENT_NAME=test-agent SECURICS_AGENT_GROUP=test-group ENROLLMENT_DELAY=10" 
test "SECURICS_MANAGER SECURICS_MANAGER_PORT SECURICS_PROTOCOL SECURICS_REGISTRATION_SERVER SECURICS_REGISTRATION_PORT SECURICS_REGISTRATION_PASSWORD SECURICS_KEEP_ALIVE_INTERVAL SECURICS_TIME_RECONNECT SECURICS_REGISTRATION_CA SECURICS_REGISTRATION_CERTIFICATE SECURICS_REGISTRATION_KEY SECURICS_AGENT_NAME SECURICS_AGENT_GROUP ENROLLMENT_DELAY " 
remove_securics

install_securics "SECURICS_MANAGER=1.1.1.1"
test "SECURICS_MANAGER "
remove_securics

install_securics "SECURICS_MANAGER_PORT=7777"
test "SECURICS_MANAGER_PORT "
remove_securics

install_securics "SECURICS_PROTOCOL=udp"
test "SECURICS_PROTOCOL "
remove_securics

install_securics "SECURICS_REGISTRATION_SERVER=2.2.2.2"
test "SECURICS_REGISTRATION_SERVER "
remove_securics

install_securics "SECURICS_REGISTRATION_PORT=8888"
test "SECURICS_REGISTRATION_PORT "
remove_securics

install_securics "SECURICS_REGISTRATION_PASSWORD=password"
test "SECURICS_REGISTRATION_PASSWORD "
remove_securics

install_securics "SECURICS_KEEP_ALIVE_INTERVAL=10"
test "SECURICS_KEEP_ALIVE_INTERVAL "
remove_securics

install_securics "SECURICS_TIME_RECONNECT=10"
test "SECURICS_TIME_RECONNECT "
remove_securics

install_securics "SECURICS_REGISTRATION_CA=/var/ossec/etc/testsslmanager.cert"
test "SECURICS_REGISTRATION_CA "
remove_securics

install_securics "SECURICS_REGISTRATION_CERTIFICATE=/var/ossec/etc/testsslmanager.cert"
test "SECURICS_REGISTRATION_CERTIFICATE "
remove_securics

install_securics "SECURICS_REGISTRATION_KEY=/var/ossec/etc/testsslmanager.key"
test "SECURICS_REGISTRATION_KEY "
remove_securics

install_securics "SECURICS_AGENT_NAME=test-agent"
test "SECURICS_AGENT_NAME "
remove_securics

install_securics "SECURICS_AGENT_GROUP=test-group"
test "SECURICS_AGENT_GROUP "
remove_securics

install_securics "ENROLLMENT_DELAY=10"
test "ENROLLMENT_DELAY "
remove_securics
