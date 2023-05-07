#! /bin/bash

if command -v yum &> /dev/null; then
    sudo yum install python3
    sudo yum install python3-pip
elif command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install python3
    sudo apt-get install python3-pip
else
    echo "Error: Unsupported Linux distribution"
    exit 1
fi

pip3 install -r requirements.txt
