#!/bin/bash

# Make sure we are on the correct einstein-ait-prod repository (https://github.com/ait-protocol/einstein-ait-prod.git)
# If not, then exit the script
if [ "$(basename `git rev-parse --show-toplevel`)" != "einstein-ait-prod" ]; then
    echo "Please make sure you are in the einstein-ait-prod repository"
    exit 1
else
    echo "You are in the einstein-ait-prod repository"
fi

# Checkout to the main branch
git checkout main

# Pull the latest changes from the main branch
git pull

# Run the bash install.sh script
bash scripts/install.sh

# Check if the einstein-ait-prod repository is up to date if it is up to date, let them know
if [ "$(git rev-parse HEAD)" != "$(git ls-remote origin -h refs/heads/main | cut -f1)" ]; then
    echo "Please make sure you have the latest changes from the main branch"
    exit 1
else
    echo "You have the latest changes from the main branch"
fi

# Check if the mathgenerator is installed
if ! pip show mathgenerator; then
    echo "Please make sure mathgenerator is installed"
    exit 1
else
    echo "mathgenerator is installed"
fi