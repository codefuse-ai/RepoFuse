#!/bin/bash
source script.sh
source ./lib/utils.sh
. ./lib/hello.bash
bash ./lib/source.bash

# Optionally load config if it exists
if [ -f "config.sh" ]; then
  source config.sh
fi

echo "Main script running"
hello
greet "User"
lib_hello
