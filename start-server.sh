#!/bin/bash

echo "Starting EventMan RomHack edition..."
echo "----------"

cd ./eventman-RomHack-edition/

while true; do
 ./eventman_server.py || exit 1
done

echo "----------"
echo "bye Saiyan ;)"
echo
