#!/usr/bin/env bash

cur_dir=$(cd $(dirname ${0});pwd)

me=$(basename $0)
cd ${cur_dir}
begin_scripts=$(ls begin_check_*.sh | grep -v ${me})
log_path=/opt/log/ops/checkall.log
echo -e "$(date)\nbegin check all..." >> ${log_path}

for script in ${begin_scripts[@]}; do
    echo -e "$(date)\nbegin check ${script}..." >> ${log_path}
    bash -x ./${script} >> ${log_path} 2>&1  &
done

wait
echo -e "$(date)\nend check all..." >> ${log_path}
