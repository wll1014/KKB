#!/usr/bin/env bash

pid=($(ps aux | grep mqwatcher.py | grep -v "grep" | awk '{print $2}'))

if [ ${#pid[@]} -ge 1 ];then
    echo -e "$(date)\nmqwatcher(${pid[@]}) is running..."
    exit 0
else
    echo -e "$(date)\nmqwatcher is not running..."
    exit 1
fi
