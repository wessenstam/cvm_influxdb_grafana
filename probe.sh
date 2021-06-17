#!/usr/bin/env sh

# Script to pull the latest of the web_server into the container on start
mkdir /code

# Start the application
python3 /code/probe.py