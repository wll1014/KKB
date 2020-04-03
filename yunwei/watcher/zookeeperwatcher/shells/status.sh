#!/usr/bin/env bash

# @author: shanchenglong
# @time: 2019/07/17

proc=$(ps aux | grep ZookeeperWatcher | grep -v grep | wc -l)

if [ ${proc} -eq 1 ]; then
    exit 0
else
    exit 1
fi