#!/bin/sh

# Copyright (C) 2023-2024, RV Bionics Group SpA.
# Shell script update functions for Securics
# Author: Daniel B. Cid <daniel.cid@gmail.com>

FALSE="false"
TRUE="true"

doUpdatecleanup()
{
    if [ "X$INSTALLDIR" = "X" ]; then
        echo "# ($FUNCNAME) ERROR: The variable INSTALLDIR wasn't set." 1>&2
        echo "${FALSE}"
        return 1;
    fi

    # Checking if the directory is valid.
    _dir_pattern_update="^/[-a-zA-Z0-9/\.-]{3,128}$"
    echo $INSTALLDIR | grep -E "$_dir_pattern_update" > /dev/null 2>&1
    if [ ! $? = 0 ]; then
        echo "# ($FUNCNAME) ERROR: directory name ($INSTALLDIR) doesn't match the pattern $_dir_pattern_update" 1>&2
        echo "${FALSE}"
        return 1;
    fi
}

##########
# Checks if Securics is installed by taking the installdir from the services
# files (if exists) and taking into account the installation type.
#
# getPreinstalledDirByType()
##########
getPreinstalledDirByType()
{
    # Checking for Systemd
    if hash ps 2>&1 > /dev/null && hash grep 2>&1 > /dev/null && [ -n "$(ps -e | egrep ^\ *1\ .*systemd$)" ]; then

        SED_EXTRACT_PREINSTALLEDDIR="s/^ExecStart=\/usr\/bin\/env \(.*\)\/bin\/securics-control start$/\1/p"

        if [ "X$pidir_service_name" = "Xsecurics-manager" ] || [ "X$pidir_service_name" = "Xsecurics-local" ]; then #manager, hibrid or local
            type="manager"
        else
            type="agent"
        fi

        # Get the unit file and extract the Securics home path
        PREINSTALLEDDIR=$(systemctl cat securics-${type}.service 2>/dev/null | sed -n "${SED_EXTRACT_PREINSTALLEDDIR}")
        if [ -n "${PREINSTALLEDDIR}" ] && [ -d "${PREINSTALLEDDIR}" ]; then
            return 0;
        fi

        # If fail, find the service file
        # RHEL 8 / Amazon / openSUSE Tumbleweed the services should be installed in /usr/lib/systemd/system/
        if [ -f /usr/lib/systemd/system/securics-${type}.service ]; then
            SERVICE_UNIT_PATH=/usr/lib/systemd/system/securics-${type}.service
        fi
        # Others
        if [ -f /etc/systemd/system/securics-${type}.service ]; then
            SERVICE_UNIT_PATH=/etc/systemd/system/securics-${type}.service
        fi

        if [ -f "$SERVICE_UNIT_PATH" ]; then
            PREINSTALLEDDIR=$(sed -n "${SED_EXTRACT_PREINSTALLEDDIR}" "${SERVICE_UNIT_PATH}")
            if [ -d "$PREINSTALLEDDIR" ]; then
                return 0;
            else
                return 1;
            fi
        else
            return 1;
        fi
    fi
    # Checking for Redhat system.
    if [ -r "/etc/redhat-release" ]; then
        if [ -d /etc/rc.d/init.d ]; then
            if [ -f /etc/rc.d/init.d/${pidir_service_name} ]; then
                PREINSTALLEDDIR=`sed -n 's/^SECURICS_HOME=\(.*\)$/\1/p' /etc/rc.d/init.d/${pidir_service_name}`
                if [ -d "$PREINSTALLEDDIR" ]; then
                    return 0;
                else
                    return 1;
                fi
            else
                return 1;
            fi
        fi
    fi
    # Checking for Gentoo
    if [ -r "/etc/gentoo-release" ]; then
        if [ -f /etc/init.d/${pidir_service_name} ]; then
            PREINSTALLEDDIR=`sed -n 's/^SECURICS_HOME=\(.*\)$/\1/p' /etc/init.d/${pidir_service_name}`
            if [ -d "$PREINSTALLEDDIR" ]; then
                return 0;
            else
                return 1;
            fi
        else
            return 1;
        fi
    fi
    # Checking for Suse
    if [ -r "/etc/SuSE-release" ]; then
        if [ -f /etc/init.d/${pidir_service_name} ]; then
            PREINSTALLEDDIR=`sed -n 's/^SECURICS_HOME=\(.*\)$/\1/p' /etc/init.d/${pidir_service_name}`
            if [ -d "$PREINSTALLEDDIR" ]; then
                return 0;
            else
                return 1;
            fi
        else
            return 1;
        fi
    fi
    # Checking for Slackware
    if [ -r "/etc/slackware-version" ]; then
        if [ -f /etc/rc.d/rc.${pidir_service_name} ]; then
            PREINSTALLEDDIR=`sed -n 's/^SECURICS_HOME=\(.*\)$/\1/p' /etc/rc.d/rc.${pidir_service_name}`
            if [ -d "$PREINSTALLEDDIR" ]; then
                return 0;
            else
                return 1;
            fi
        else
            return 1;
        fi
    fi
    # Checking for Darwin
    if [ "X${NUNAME}" = "XDarwin" ]; then
        if [ -f /Library/StartupItems/SECURICS/SECURICS ]; then
            PREINSTALLEDDIR=`sed -n 's/^ *//; s/^\s*\(.*\)\/bin\/securics-control start$/\1/p' /Library/StartupItems/SECURICS/SECURICS`
            if [ -d "$PREINSTALLEDDIR" ]; then
                return 0;
            else
                return 1;
            fi
        else
            return 1;
        fi
    fi
    # Checking for SunOS
    if [ "X${UN}" = "XSunOS" ]; then
        if [ -f /etc/init.d/${pidir_service_name} ]; then
            PREINSTALLEDDIR=`sed -n 's/^SECURICS_HOME=\(.*\)$/\1/p' /etc/init.d/${pidir_service_name}`
            if [ -d "$PREINSTALLEDDIR" ]; then
                return 0;
            else
                return 1;
            fi
        else
            return 1;
        fi
    fi
    # Checking for HP-UX
    if [ "X${UN}" = "XHP-UX" ]; then
        if [ -f /sbin/init.d/${pidir_service_name} ]; then
            PREINSTALLEDDIR=`sed -n 's/^SECURICS_HOME=\(.*\)$/\1/p' /sbin/init.d/${pidir_service_name}`
            if [ -d "$PREINSTALLEDDIR" ]; then
                return 0;
            else
                return 1;
            fi
        else
            return 1;
        fi
    fi
    # Checking for AIX
    if [ "X${UN}" = "XAIX" ]; then
        if [ -f /etc/rc.d/init.d/${pidir_service_name} ]; then
            PREINSTALLEDDIR=`sed -n 's/^SECURICS_HOME=\(.*\)$/\1/p' /etc/rc.d/init.d/${pidir_service_name}`
            if [ -d "$PREINSTALLEDDIR" ]; then
                return 0;
            else
                return 1;
            fi
        else
            return 1;
        fi
    fi
    # Checking for BSD
    if [ "X${UN}" = "XOpenBSD" -o "X${UN}" = "XNetBSD" -o "X${UN}" = "XFreeBSD" -o "X${UN}" = "XDragonFly" ]; then
        # Checking for the presence of securics-control on rc.local
        grep securics-control /etc/rc.local > /dev/null 2>&1
        if [ $? = 0 ]; then
            PREINSTALLEDDIR=`sed -n 's/^\(.*\)\/bin\/securics-control start$/\1/p' /etc/rc.local`
            if [ -d "$PREINSTALLEDDIR" ]; then
                return 0;
            else
                return 1;
            fi
        else
            return 1;
        fi
    elif [ "X${NUNAME}" = "XLinux" ]; then
        # Checking for Linux
        if [ -e "/etc/rc.d/rc.local" ]; then
            grep securics-control /etc/rc.d/rc.local > /dev/null 2>&1
            if [ $? = 0 ]; then
                PREINSTALLEDDIR=`sed -n 's/^\(.*\)\/bin\/securics-control start$/\1/p' /etc/rc.d/rc.local`
                if [ -d "$PREINSTALLEDDIR" ]; then
                    return 0;
                else
                    return 1;
                fi
            else
                return 1;
            fi
        # Checking for Linux (SysV)
        elif [ -d "/etc/rc.d/init.d" ]; then
            if [ -f /etc/rc.d/init.d/${pidir_service_name} ]; then
                PREINSTALLEDDIR=`sed -n 's/^SECURICS_HOME=\(.*\)$/\1/p' /etc/rc.d/init.d/${pidir_service_name}`
                if [ -d "$PREINSTALLEDDIR" ]; then
                    return 0;
                else
                    return 1;
                fi
            else
                return 1;
            fi
        # Checking for Debian (Ubuntu or derivative)
        elif [ -d "/etc/init.d" -a -f "/usr/sbin/update-rc.d" ]; then
            if [ -f /etc/init.d/${pidir_service_name} ]; then
                PREINSTALLEDDIR=`sed -n 's/^SECURICS_HOME=\(.*\)$/\1/p' /etc/init.d/${pidir_service_name}`
                if [ -d "$PREINSTALLEDDIR" ]; then
                    return 0;
                else
                    return 1;
                fi
            else
                return 1;
            fi
        fi
    fi

    return 1;
}

##########
# Checks if Securics is installed in the specified path by searching for the control binary.
#
# isSecuricsInstalled()
##########
isSecuricsInstalled()
{
    if [ -f "${1}/bin/securics-control" ]; then
        return 0;
    elif [ -f "${1}/bin/ossec-control" ]; then
        return 0;
    else
        return 1;
    fi
}

##########
# Checks if Securics is installed by trying with each installation type.
# If it finds an installation, it sets the PREINSTALLEDDIR variable.
# After that it checks if Securics is truly installed there, if it is installed it returns TRUE.
# If it isn't installed continue searching in other installation types and replacing PREINSTALLEDDIR variable.
# It returns FALSE if Securics isn't installed in any of this.
#
# getPreinstalledDir()
##########
getPreinstalledDir()
{
    # Checking ossec-init.conf for old securics versions
    if [ -f "${OSSEC_INIT}" ]; then
        . ${OSSEC_INIT}
        if [ -d "$DIRECTORY" ]; then
            PREINSTALLEDDIR="$DIRECTORY"
            if isSecuricsInstalled $PREINSTALLEDDIR; then
                return 0;
            fi
        fi
    fi

    # Getting preinstalled dir for Securics manager and hibrid installations
    pidir_service_name="securics-manager"
    if getPreinstalledDirByType && isSecuricsInstalled $PREINSTALLEDDIR; then
        return 0;
    fi

    # Getting preinstalled dir for Securics agent installations
    pidir_service_name="securics-agent"
    if getPreinstalledDirByType && isSecuricsInstalled $PREINSTALLEDDIR; then
        return 0;
    fi

    # Getting preinstalled dir for Securics local installations
    pidir_service_name="securics-local"
    if getPreinstalledDirByType && isSecuricsInstalled $PREINSTALLEDDIR; then
        return 0;
    fi

    return 1;
}

getPreinstalledType()
{
    # Checking ossec-init.conf for old securics versions
    if [ -f "${OSSEC_INIT}" ]; then
        . ${OSSEC_INIT}
    else
        if [ "X$PREINSTALLEDDIR" = "X" ]; then
            getPreinstalledDir
        fi

        TYPE=`$PREINSTALLEDDIR/bin/securics-control info -t`
    fi

    echo $TYPE
    return 0;
}

getPreinstalledVersion()
{
    # Checking ossec-init.conf for old securics versions
    if [ -f "${OSSEC_INIT}" ]; then
        . ${OSSEC_INIT}
    else
        if [ "X$PREINSTALLEDDIR" = "X" ]; then
            getPreinstalledDir
        fi

        VERSION=`$PREINSTALLEDDIR/bin/securics-control info -v`
    fi

    echo $VERSION
}

getPreinstalledName()
{
    NAME=""
    # Checking ossec-init.conf for old securics versions. New versions
    # do not provide this information at all.
    if [ -f "${OSSEC_INIT}" ]; then
        . ${OSSEC_INIT}
    else
        NAME="Securics"
    fi

    echo $NAME
}

UpdateStartOSSEC()
{
    if [ "X$TYPE" = "X" ]; then
        getPreinstalledType
    fi

    if [ "X$TYPE" != "Xagent" ]; then
        TYPE="manager"
    fi

    if [ `stat /proc/1/exe 2> /dev/null | grep "systemd" | wc -l` -ne 0 ]; then
        systemctl start securics-$TYPE
    elif [ `stat /proc/1/exe 2> /dev/null | grep "init.d" | wc -l` -ne 0 ]; then
        service securics-$TYPE start
    else
        # Considering that this function is only used after finishing the installation
        # the INSTALLDIR variable is always set. It could have either the default value,
        # or a value equals to the PREINSTALLEDDIR, or a value specified by the user.
        # The last two possibilities are set in the setInstallDir function.
        $INSTALLDIR/bin/securics-control start
    fi
}

UpdateStopOSSEC()
{
    MAJOR_VERSION=`echo ${VERSION} | cut -f1 -d'.' | cut -f2 -d'v'`

    if [ "X$TYPE" = "X" ]; then
        getPreinstalledType
    fi

    if [ "X$TYPE" != "Xagent" ]; then
        TYPE="manager"
        if [ $MAJOR_VERSION -ge 4 ]; then
            EMBEDDED_API_INSTALLED=1
        fi
    fi

    if [ `stat /proc/1/exe 2> /dev/null | grep "systemd" | wc -l` -ne 0 ]; then
        systemctl stop securics-$TYPE
    elif [ `stat /proc/1/exe 2> /dev/null | grep "init.d" | wc -l` -ne 0 ]; then
        service securics-$TYPE stop
    fi

    # Make sure Securics is stopped
    if [ "X$PREINSTALLEDDIR" = "X" ]; then
        getPreinstalledDir
    fi

    if [ -f "$PREINSTALLEDDIR/bin/ossec-control" ]; then
        $PREINSTALLEDDIR/bin/ossec-control stop > /dev/null 2>&1
    else
        $PREINSTALLEDDIR/bin/securics-control stop > /dev/null 2>&1
    fi

    sleep 2

   # We also need to remove all syscheck queue file (format changed)
    if [ "X$VERSION" = "X0.9-3" ]; then
        rm -f $PREINSTALLEDDIR/queue/syscheck/* > /dev/null 2>&1
        rm -f $PREINSTALLEDDIR/queue/agent-info/* > /dev/null 2>&1
    fi
    rm -rf $PREINSTALLEDDIR/framework/* > /dev/null 2>&1
    rm $PREINSTALLEDDIR/wodles/aws/aws > /dev/null 2>&1 # this script has been renamed
    rm $PREINSTALLEDDIR/wodles/aws/aws.py > /dev/null 2>&1 # this script has been renamed

    # Deleting plain-text agent information if exists (it was migrated to Securics DB in v4.1)
    if [ -d "$PREINSTALLEDDIR/queue/agent-info" ]; then
        rm -rf $PREINSTALLEDDIR/queue/agent-info > /dev/null 2>&1
    fi

    # Deleting plain-text rootcheck information if exists (it was migrated to Securics DB in v4.1)
    if [ -d "$PREINSTALLEDDIR/queue/rootcheck" ]; then
        rm -rf $PREINSTALLEDDIR/queue/rootcheck > /dev/null 2>&1
    fi

    # Deleting groups backup folder if exists
    if [ -d "$PREINSTALLEDDIR/backup/groups" ]; then
        rm -rf $PREINSTALLEDDIR/backup/groups > /dev/null 2>&1
    fi
}

UpdateOldVersions()
{
    if [ "$INSTYPE" = "server" ]; then
        # Delete deprecated rules & decoders
        echo "Searching for deprecated rules and decoders..."
        DEPRECATED=`cat ./src/init/securics/deprecated_ruleset.txt`
        for i in $DEPRECATED; do
            DEL_FILE="$INSTALLDIR/ruleset/$i"
            if [ -f ${DEL_FILE} ]; then
                echo "Deleting '${DEL_FILE}'."
                rm -f ${DEL_FILE}
            fi
        done
    fi

    # If it is Securics 2.0 or newer, exit
    if [ "X$USER_OLD_NAME" = "XSecurics" ]; then
        return
    fi

    if [ "X$PREINSTALLEDDIR" != "X" ]; then
        getPreinstalledDir
    fi

    OSSEC_CONF_FILE="$PREINSTALLEDDIR/etc/ossec.conf"
    OSSEC_CONF_FILE_ORIG="$PREINSTALLEDDIR/etc/ossec.conf.orig"

    # ossec.conf -> ossec.conf.orig
    cp -pr $OSSEC_CONF_FILE $OSSEC_CONF_FILE_ORIG

    # Delete old service
    if [ -f /etc/init.d/ossec ]; then
        rm /etc/init.d/ossec
    fi

    if [ ! "$INSTYPE" = "agent" ]; then

        # Delete old update ruleset
        if [ -d "$PREINSTALLEDDIR/update" ]; then
            rm -rf "$PREINSTALLEDDIR/update"
        fi

        ETC_DECODERS="$PREINSTALLEDDIR/etc/decoders"
        ETC_RULES="$PREINSTALLEDDIR/etc/rules"

        # Moving local_decoder
        if [ -f "$PREINSTALLEDDIR/etc/local_decoder.xml" ]; then
            if [ -s "$PREINSTALLEDDIR/etc/local_decoder.xml" ]; then
                mv "$PREINSTALLEDDIR/etc/local_decoder.xml" $ETC_DECODERS
            else
                # it is empty
                rm -f "$PREINSTALLEDDIR/etc/local_decoder.xml"
            fi
        fi

        # Moving local_rules
        if [ -f "$PREINSTALLEDDIR/rules/local_rules.xml" ]; then
            mv "$PREINSTALLEDDIR/rules/local_rules.xml" $ETC_RULES
        fi

        # Creating backup directory
        BACKUP_RULESET="$PREINSTALLEDDIR/etc/backup_ruleset"
        mkdir $BACKUP_RULESET > /dev/null 2>&1
        chmod 750 $BACKUP_RULESET > /dev/null 2>&1
        chown root:securics $BACKUP_RULESET > /dev/null 2>&1

        # Backup decoders: Securics v1.0.1 to v1.1.1
        old_decoders="ossec_decoders securics_decoders"
        for old_decoder in $old_decoders
        do
            if [ -d "$PREINSTALLEDDIR/etc/$old_decoder" ]; then
                mv "$PREINSTALLEDDIR/etc/$old_decoder" $BACKUP_RULESET
            fi
        done

        # Backup decoders: Securics v1.0 and OSSEC
        if [ -f "$PREINSTALLEDDIR/etc/decoder.xml" ]; then
            mv "$PREINSTALLEDDIR/etc/decoder.xml" $BACKUP_RULESET
        fi

        # Backup rules: All versions
        mv "$PREINSTALLEDDIR/rules" $BACKUP_RULESET

        # New ossec.conf by default
        ./gen_ossec.sh conf "manager" $DIST_NAME $DIST_VER > $OSSEC_CONF_FILE
        ./add_localfiles.sh $PREINSTALLEDDIR >> $OSSEC_CONF_FILE
    else
        # New ossec.conf by default
        ./gen_ossec.sh conf "agent" $DIST_NAME $DIST_VER > $OSSEC_CONF_FILE
        # Replace IP
        ./src/init/replace_manager_ip.sh $OSSEC_CONF_FILE_ORIG $OSSEC_CONF_FILE
        ./add_localfiles.sh $PREINSTALLEDDIR >> $OSSEC_CONF_FILE
    fi
}
