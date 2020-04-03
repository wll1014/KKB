#!/usr/bin/env bash

pid=$(ps aux | grep mqwatcher.py | grep -v "grep" | awk '{print $2}')

if [ -z "${pid}" ];then
    echo -e "$(date)\nmqwatcher is not running..."
else
    kill -9 ${pid}
    echo -e "$(date)\nmqwatcher(${pid}) is killed..."
fi

