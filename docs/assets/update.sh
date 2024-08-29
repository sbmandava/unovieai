#!/bin/bash

mytmp=$(mktemp -d)
LOG_FILE=/tmp/sandbox.log


## Check if we are running with sudo privileges
if [ "$(id -u)" != "0" ]; then
  # If not, print an error message and exit
  echo "Error: This script must be run with sudo privileges."
  echo "Please run the script again with 'sudo' at the beginning of the command:"
  echo "    sudo $0"
  exit 1
fi

check_capacity()
{
# Check if the OS is Ubuntu 24.04
if [ "$(lsb_release -a | grep "Ubuntu 24.04")" != "" ]; then
  :
else
  echo "Error: This script must be run on an Ubuntu 24.04 system."
  exit 1
fi

# Check if the system has at least 8GB of memory
if [ $(free -b | awk '/Mem:/ {print $2}') -lt 8024967296 ]; then
  echo "Error: This script requires a system with at least 8GB of memory."
  exit 1
fi

# Check if /opt has at least 40GB of disk space
if [ $(df -P /opt | awk '/%/ {print $4}') -lt 40828596 ]; then
  echo "Error: This script requires a system with at least 40GB of free disk space in the /opt directory."
  exit 1
fi

# If all checks pass, print success message and continue execution
echo "System meets all requirements. Proceeding..."
}

add_postgresml()
{
mkdir /tmp/update.v1
cd /tmp/update.v1
wget https://unovie.ai/docs/assets/updates.v1.tgz
tar -xvzf updates.v1.tgz
cd updates
mv tools /opt
mv postgresml /opt
cd /tmp
rm -rf /tmp/update.v1
}


### Main ###

add_postgresml
echo "------------------------------------------------------------------"
echo "update v1 installed... "
echo "------------------------------------------------------------------"
echo "postgresml installed in /opt/postgresml"
echo "tools installed in /opt/tools"
echo " "
echo "Going forward use start stop scripts in /opt/tools/"
echo " "
echo "Note : You may want to shutdown DIFY when running PGML"
echo "and likewise the otherway around for better optimal performance"
echo "------------------------------------------------------------------"
