#!/usr/bin/env bash

# @author: shanchenglong
# @time: 2019/07/17

moid=$1
cfg_path=/opt/data/config/${moid}/zookeeperwatcher/currConf.ini
des_path=/opt/datawatcher/zookeeperwatcher/conf/ZKWatcher.ini

if [ -f ${cfg_path} ]; then
    \cp -a ${cfg_path} ${des_path}
    exit $?
else
    exit 1
fi
