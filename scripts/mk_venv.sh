#!/bin/bash

# Get script directory absolute path. This way script always runs as if from within 'scripts/' dir.
scriptDir=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
cd "$scriptDir"

# Get out of script directory
cd ..

# Setup virtual env in used-entered directory of project.
while true; do
    read -p "Which directory do you wish to setup virtualenv?" answer
    if [ -d "$answer" ]; then
        cd "$answer" && break
    else
        echo "Please enter a valid directory."
    fi
done
virtualenv --python=python3.5 venv
cd ..