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

# Check if the system has at least 4GB of memory
if [ $(free -b | awk '/Mem:/ {print $2}') -lt 4024967296 ]; then
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

setup_user ()
{
# Set variables for the new user's details
USERNAME="unovie"
PASSWORD="unovie2024"

# Add the new user
sudo useradd -m --shell=/bin/bash $USERNAME

# Set the password for the new user
echo "$USERNAME:$PASSWORD" | sudo chpasswd

# Grant sudo privileges to the new user
sudo usermod -aG sudo $USERNAME

# Print a success message
echo "User added and granted sudo privileges successfully!"
}

add_packages ()
{
apt-get -y update;apt-get -y upgrade
apt-get install -y openssh-server wget curl git sudo build-essential
apt-get remove -y podman-docker podman-compose  
apt-get install -y docker.io  docker-compose-v2
apt-get install -y python3-distutils-extra jq
cd /tmp
wget -q https://github.com/docker/compose/releases/download/v2.29.2/docker-compose-linux-x86_64
mv docker-compose-linux-x86_64 /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
}

install_kg ()
{
mkdir -p /opt/projects
cd /tmp
wget --no-check-certificate https://unovie.ai/repo/sales-kg-run.tgz
cd /opt/projects
tar -xvzf /tmp/sales-kg-run.tgz 
}


### Main ###

echo "please..wait takes about 10 minutes to install..get a coffee break"
echo "All script results are written to logfile $LOG_FILE"
check_capacity
setup_user
echo "...adding deb packages"
add_packages 2>&1 >$LOG_FILE
install_kg 2>&1 >>$LOG_FILE

echo "------------------------------------------------------------------"
echo "Installation done in /opt/projects/sales-kg-run"
echo "Follow README.md and INSTALL.MD for further instructions" 
echo " "
echo "Required software installed installed : docker, docker-compose"
echo "You might want to logout and login again or reboot to make sure profile is loaded"
echo " "
echo "------------------------------------------------------------------"
