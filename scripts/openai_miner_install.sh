#!/bin/bash

# Installing package from the current directory
pip install -e .

# Uninstalling mathgenerator
pip uninstall mathgenerator -y

# Reinstalling requirements to ensure mathgenerator is installed appropriately
pip install -r requirements.txt

# Uninstalling uvloop to prevent conflicts with bittensor
pip uninstall uvloop -y

# Reinstalling pydantic and transformers with specific versions that work with our repository and vllm
pip install pydantic==1.10.7 transformers==4.36.2

# echo 
echo -e "\e[1;32mThe Error on pip's dependency resolver is bound to happen, do not worry, this is normal behavior\e[0m"

# Installing openai miner
pip install -r neurons/miners/openai/requirements.txt
