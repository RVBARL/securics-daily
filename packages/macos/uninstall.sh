#!/bin/sh

## Stop and remove application
sudo /Library/Ossec/bin/securics-control stop
sudo /bin/rm -r /Library/Ossec*

# remove launchdaemons
/bin/rm -f /Library/LaunchDaemons/com.securics.agent.plist

## remove StartupItems
/bin/rm -rf /Library/StartupItems/SECURICS

## Remove User and Groups
/usr/bin/dscl . -delete "/Users/securics"
/usr/bin/dscl . -delete "/Groups/securics"

/usr/sbin/pkgutil --forget com.securics.pkg.securics-agent
/usr/sbin/pkgutil --forget com.securics.pkg.securics-agent-etc

# In case it was installed via Puppet pkgdmg provider

if [ -e /var/db/.puppet_pkgdmg_installed_securics-agent ]; then
    rm -f /var/db/.puppet_pkgdmg_installed_securics-agent
fi

echo
echo "Securics agent correctly removed from the system."
echo

exit 0
