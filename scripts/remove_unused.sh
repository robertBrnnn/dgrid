#!/usr/bin/env bash
# Copied from http://stackoverflow.com/questions/32723111/how-to-remove-old-and-unused-docker-images
# SO User: Ell Neal

# Remove all the dangling images
DANGLING_IMAGES=$(docker images -qf "dangling=true")
if [[ -n $DANGLING_IMAGES ]]; then
    echo "Dangling images to be removed: "
    echo $DANGLING_IMAGES
    docker rmi "$DANGLING_IMAGES"
fi

# Get all the images currently in use
USED_IMAGES=($( \
    docker ps -a --format '{{.Image}}' | \
    sort -u | \
    uniq | \
    awk -F ':' '$2{print $1":"$2}!$2{print $1":latest"}' \
))

# Get all the images currently available
ALL_IMAGES=($( \
    docker images --format '{{.Repository}}:{{.Tag}}' | \
    sort -u \
))

# Remove the unused images
for i in "${ALL_IMAGES[@]}"; do
    UNUSED=true
    for j in "${USED_IMAGES[@]}"; do
        if [[ "$i" == "$j" ]]; then
            UNUSED=false
        fi
    done
    if [[ "$UNUSED" == true ]]; then
        echo "Removing image: "
        echo $i
        docker rmi "$i"
    fi
done