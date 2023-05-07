#! /bin/bash

cd src/

# Set up logging
mkdir -p logs
touch logs/app.log

nohup python3 dbot.py &> logs/app.log 2>&1 &
