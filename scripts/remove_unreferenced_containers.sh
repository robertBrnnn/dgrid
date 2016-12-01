#!/usr/bin/env bash
# Author: Robert Brennan
# Removes containers that use unreferenced images

# Get unreferenced images
URI=$(docker images -q -f dangling=true)
echo $URI
for i in $URI; do
    # Get containers using unreferenced images
    images_to_remove=$(docker ps -a | grep $i | awk '{print $1}')
    for j in $images_to_remove; do
        # Remove container
        docker rm -fv $j
    done
done
