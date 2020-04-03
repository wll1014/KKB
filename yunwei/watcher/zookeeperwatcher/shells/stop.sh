#!/usr/bin/env bash

# @author: shanchenglong
# @time: 2019/07/17

pid=$(ps aux | grep ZookeeperWatcher | grep -v grep | column -t | cut -d" " -f3)

if [ -z "${pid}" ]; then
    exit 0
else
    kill -9 ${pid}
fi