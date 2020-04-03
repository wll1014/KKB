#!/usr/bin/env bash

elasticdump_pids=$(ps -ef | grep "node" | grep "elasticdump" | grep ".json" | grep -v "grep" | awk '{print $2}')
if [ -n "${elasticdump_pids}" ];then
    kill ${elasticdump_pids}
else
    echo "elasticdump is not running..."
fi

check_dump_pids=$(ps -ef | grep "check_dump.sh" | grep "bash" | grep -v "grep" | awk '{print $2}')
if [ -n "${check_dump_pids}" ];then
    kill ${check_dump_pids}
else
    echo "check_dump.sh is not running..."
fi

exit 0