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

add_anaconda()
{
## Install Anaconda 
cd $mytmp
wget -q https://repo.anaconda.com/archive/Anaconda3-2024.06-1-Linux-x86_64.sh
chmod +x Anaconda3-2024.06-1-Linux-x86_64.sh
./Anaconda3-2024.06-1-Linux-x86_64.sh -p /opt/conda -b
echo "source /opt/conda/etc/profile.d/conda.sh" > /opt/python.env
echo 'source /opt/conda/etc/profile.d/conda.sh' >> ~/.bashrc
echo 'conda activate llm' >> ~/.bashrc
}

install_llm ()
{
source /opt/conda/etc/profile.d/conda.sh
conda create -n llm python=3.11 -y
conda activate llm
pip install llm
llm install llm-ollama
llm install llm-gemini
llm install llm-sentence-transformers
llm embed -m sentence-transformers/all-MiniLM-L6-v2 -c 'hello world'
llm install llm-embed-jina
llm embed -m jina-embeddings-v2-small-en -c 'Hello world'
apt-get install -y libcurl4-openssl-dev libgomp1
# pip install txtai torch==2.5+cpu -f https://download.pytorch.org/whl/torch 
# CMAKE_ARGS='-D CMAKE_C_FLAGS="-fopenmp" -D CMAKE_CXX_FLAGS="-fopenmp"' pip install llama-cpp-python --no-cache-dir --force-reinstall
CMAKE_ARGS='-D CMAKE_C_FLAGS="-fopenmp" -D CMAKE_CXX_FLAGS="-fopenmp"' pip install txtai[all]
pip install aider-install
aider-install
echo 'export PATH="$PATH:/root/.local/bin"' >> ~/.bashrc
source ~/.bashrc
}

### Main ###

echo "please..wait takes about 10 minutes to install..get a coffee break"
echo "All script results are written to logfile $LOG_FILE"
check_capacity
setup_user
echo "...adding deb packages"
add_packages 2>&1 >$LOG_FILE
echo "...installing anaconda"
add_anaconda 2>&1 >>$LOG_FILE
install_llm 2>&1 >>$LOG_FILE

echo "------------------------------------------------------------------"
echo "Installation done for sandbox llm"
echo "Software installed : conda, docker, docker-compose,txtai,llm , aider"
echo "You might want to logout and login again or reboot to make sure profile is loaded"
echo "------------------------------------------------------------------"
