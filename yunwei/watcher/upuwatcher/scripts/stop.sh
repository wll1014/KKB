#!/usr/bin/env bash

pid=$(ps aux | grep upu_watcher | grep -v "grep" | awk '{print $2}')

if [ -z ${pid} ];then
    echo -e "$(date)\nupu_watcher is not running..."
else
    kill -9 ${pid}
    echo -e "$(date)\nupu_watcher(${pid}) is killed..."
fi

