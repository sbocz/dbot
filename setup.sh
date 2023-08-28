#! /bin/bash

if command -v yum &> /dev/null; then
    sudo amazon-linux-extras install epel -y
    sudo yum install python38 -y
    sudo yum install python38-pip -y
    sudo alternatives --set python /usr/bin/python3.8
    if ! command -v pip3 &> /dev/null; then
        sudo ln -s /usr/bin/pip3.8 /usr/bin/pip3
    fi
elif command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install python3.8 -y
    sudo apt-get install python3-pip -y
else
    echo "Error: Unsupported Linux distribution"
    exit 1
fi

pip3.8 install -r requirements.txt
