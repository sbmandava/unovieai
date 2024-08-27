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
echo "docker run -d -p 3000:3000  ghcr.io/eclipse-theia/theia-blueprint/theia-ide:1.52.0" > /opt/web-ide.sh
chmod +x /opt/web-ide.sh
su - unovie -c "source /opt/python.env;conda create -y -n unovie310 python=3.10"
su - unovie -c "echo 'source /opt/python.env' >> ~/.bashrc"
su - unovie -c "echo 'conda config --set auto_activate_base false' >> ~/.bashrc"
su - unovie -c "echo 'conda activate unovie310' >> ~/.bashrc"
}


add_ollama_dify()
{
cd /opt;git clone https://github.com/langgenius/dify.git;
cd /opt/dify/docker;mv .env.example .env
cd /tmp;wget -q https://unovie.ai/docs/assets/docker-compose.yaml;mv /tmp/docker-compose.yaml /opt/dify/docker/
echo ".....bringing docker-compose up from /opt/dify/docker"
chown -R root:root /opt/dify/docker/volumes/*
cd /opt/dify/docker;docker-compose up -d
echo "...waiting for database initalization"
sleep 10
echo ".....downloading ai-models for ollama"
docker exec ollama ollama pull all-minilm:l6-v2
docker exec ollama ollama pull gemma2:2b-instruct-q2_K
docker exec ollama ollama cp gemma2:2b-instruct-q2_K uv-gemma2
docker exec ollama ollama pull phi3.5:3.8b-mini-instruct-q2_K
docker exec ollama ollama cp phi3.5:3.8b-mini-instruct-q2_K uv-phi35
}

fix_perms ()
{
cd /opt
chown unovie:unovie /opt
chown -R unovie:unovie /opt/*
}


### Main ###

echo "please..wait takes some time writing to logfile $LOG_FILE"
check_capacity
setup_user
echo "...adding deb packages"
add_packages 2>&1 >$LOG_FILE
echo "...installing anaconda"
add_anaconda 2>&1 >>$LOG_FILE
fix_perms  ## need to check it later..
echo "...installing ollama and dify"
add_ollama_dify 
echo "------------------------------------------------------------------"
echo "Installation done"
echo "------------------------------------------------------------------"
echo "login id: $USERNAME password: $PASSWORD"
echo "once logged in follow /opt/readme.txt for further instructions"
echo "Please refer to documentation on https://unovie.ai/docs"
echo "DIFY instance can be accessed on https://<WSL2-ip>"
echo " "
echo "Configure DIFY for these Models"
echo " .... text-embedding : all-minilm:l6-v2"
echo " .... chat : uv-gemma2"
echo " .... server : http://ollama:11434"
echo "------------------------------------------------------------------"
