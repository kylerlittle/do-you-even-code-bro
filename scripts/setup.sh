#!/bin/bash

# Get script directory absolute path. This way script always runs as if from within 'scripts/' dir.
scriptDir=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
cd "$scriptDir"

# Install Python3
sudo apt-get install libssl-dev openssl
wget https://www.python.org/ftp/python/3.5.0/Python-3.5.0.tgz
tar xzvf Python-3.5.0.tgz
cd Python-3.5.0
./configure
make
sudo make install

# Clean-up
cd ..
rm Python-3.5.0.tgz
sudo rm -rf Python-3.5.0/

# Install pip
sudo apt-get install python3-pip

# Install virtualenv
sudo pip3 install virtualenv

# Get out of script directory
cd ..

# Setup virtual env in used-entered directory of project.
while true; do
    read -p "Which directory do you wish to setup virtualenv? " answer
    if [ -d "$answer" ]; then
        cd "$answer" && break
    else
        echo "Please enter a valid directory."
    fi
done
virtualenv --python=python3.5 venv
cd ..

