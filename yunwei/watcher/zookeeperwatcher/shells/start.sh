#!/usr/bin/env bash

# @author: shanchenglong
# @time: 2019/07/17

cur_dir=$(dirname "$0")
cd ${cur_dir}

/opt/midware/python3/bin/python3 ../ZookeeperWatcher.py &
