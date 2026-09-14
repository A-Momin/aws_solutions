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
cp lambdas/lfn1/crawler_triggerer.py setup/
cd ./setup

# pip install -r ../requirements.txt -t .


# Prepares the deployment package
echo "Zipping package"
zip -r ../lambdas/lfn1/package.zip ./* 

# Remove the setup directory used
echo "Removing setup directory and virtual environment"
cd ..
rm -r ./setup
deactivate
rm -r .venv

# mv ./package.zip ./lambdas/lfn1/

# changing dirs back to dir from before
echo "Opening folder containg function package - 'package.zip'"
open ./lambdas/lfn1/package.zip

# given path for three directories  (lambda_dir, package_dir). write a python function that create a temporary directory (temp_dir) in the current directory. Create a python virtual environment and activate it and if a requirements.txt file is given it install library from the file into the activated virtual environment. copy all the contents into temp_dir and compress (zipup) it naming the compressed file package.zip and save the package.zip file inot package_dir. finally remove the virtual environment and temporary directory.