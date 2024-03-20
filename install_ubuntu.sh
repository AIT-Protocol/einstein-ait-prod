#!/bin/bash


apt-get update
apt-get install sudo

# Install python3-pip
sudo apt install -y python3-pip

# Upgrade bittensor
python3 -m pip install --upgrade bittensor

apt install tree

# Install required packages
sudo apt update && sudo apt install jq && sudo apt install npm && sudo npm install pm2 -g && pm2 update

# echo 'export OPENAI_API_KEY=YOUR_OPEN_AI_KEY' >> ~/.bashrc
# echo 'OPENAI_API_KEY=YOUR_OPEN_AI_KEY' >> ~/.env

# Clone the repository
git clone https://github.com/ait-protocol/einstein-ait-prod.git

# Change to the einstein-ait-prod directory
cd einstein-ait-prod

# Install Python dependencies
python3 -m pip install -r requirements.txt

# Install einstein-ait-prod package
python3 -m pip install -e .

echo "Script completed successfully."