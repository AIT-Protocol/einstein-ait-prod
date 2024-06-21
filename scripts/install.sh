#!/bin/bash

# Uninstalling mathgenerator
pip uninstall mathgenerator -y

# Installing package from the current directory
pip install -e .

# echo 
echo -e "\e[1;32mThe Error on pip's dependency resolver is bound to happen, do not worry, this is normal behavior\e[0m"