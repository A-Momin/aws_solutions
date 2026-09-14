#!/bin/bash

# Create and initialize a Python Virtual Environment
echo "Creating virtual environment - .venv"
python3 -m venv .venv

echo "sourcing virtual environment - .venv"
source .venv/bin/activate

# Create a directory to put things in
echo "Creating 'setup' directory"
mkdir setup

# Move the relevant files into setup directory
echo "Moving function file(s) to setup dir"
cp handlers.py setup/
cd ./setup

# Install requirements 
echo "pip installing requirements from requirements file in target directory"

#  install all the packages listed in the requirements.txt into current directory
pip install -r ../requirements.txt -t .

# Prepares the deployment package
echo "Zipping package"
zip -r ../handlers.zip ./* 

# Remove the setup directory used
echo "Removing setup directory"
cd ..
rm -r ./setup
deactivate
# rm -r .venv

# changing dirs back to dir from before
# echo "Opening folder containg function package - 'handlers.zip'"
# open .