#!/bin/bash

# Extract the arguments from command-line
arg1=$1
arg2=$2

# Build the regular expression using the Python script
regex=$(echo "$arg2" | python build.py)

# Run the Python script with the input string
echo "$arg1" | python run.py <<< "$(echo -e "${arg1}\n${regex}")"

