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
apt-get install -y openssh-server wget curl git 
apt-get remove -y podman-docker podman-compose  
apt-get install -y docker.io  
apt-get install -y python3-distutils-extra
cd /tmp
wget -q https://github.com/docker/compose/releases/download/v2.29.2/docker-compose-linux-x86_64
mv docker-compose-linux-x86_64 /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
}

add_anaconda()
{
## Install Anaconda 
cd $mytmp
wget -q https://repo.anaconda.com/archive/Anaconda3-2024.06-1-Linux-x86_64.sh
chmod +x Anaconda3-2024.06-1-Linux-x86_64.sh
./Anaconda3-2024.06-1-Linux-x86_64.sh -p /opt/conda -b
echo "source /opt/conda/etc/profile.d/conda.sh" > /opt/python.env
chmod +x /opt/web-ide.sh
}

add_sandbox3()
{
mkdir /tmp/update.v3
cd /tmp/update.v3
wget https://unovie.ai/docs/assets/updates.v3.tgz
tar -xvzf updates.v3.tgz
cd updates
mkdir /opt/tools
mkdir /opt/sandbox3
mkdir /opt/project
chmod 777 /opt/project
cp tools/* /opt/tools/
cp sandbox3/* /opt/sandbox3
cd /opt/sandbox3
docker-compose pull
cd /tmp
rm -rf /tmp/update.v3
}



### Main ###

echo "please..wait takes some time writing to logfile $LOG_FILE"
check_capacity
setup_user
echo "...adding deb packages"
add_packages 2>&1 >$LOG_FILE
echo "...installing anaconda"
add_anaconda 2>&1 >>$LOG_FILE
echo "...installing pgml"
add_sandbox3
ipa=`hostname -I`

echo "------------------------------------------------------------------"
echo "Installation done for sandbox3"
echo "------------------------------------------------------------------"
echo " Softare Installed : postgres, postgresml, pgadmin4, web-ide"
echo "------------------------------------------------------------------"
echo "Open Browser and access VM http://ip_address"
echo "Known IP address for this VM is : $ipa"
echo " "
echo "Please refer to documentation for any specific details like account id"
echo "       https://unovie.ai/docs/setup/linux-sandbox3/"
echo "------------------------------------------------------------------"
