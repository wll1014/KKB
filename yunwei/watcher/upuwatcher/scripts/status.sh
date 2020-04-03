#!/usr/bin/env bash

pid=($(ps aux | grep upu_watcher.py | grep -v "grep" | awk '{print $2}'))

if [ ${#pid[@]} -ge 1 ];then
    echo -e "$(date)\nupu_watcher(${pid[@]}) is running..."
    exit 0
else
    echo -e "$(date)\nupu_watcher is not running..."
    exit 1
fi
