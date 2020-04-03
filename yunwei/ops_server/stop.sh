#!/usr/bin/env bash

path=$(cd $(dirname $0);pwd)
pid_file=/opt/data/ops/ops.pid

# 停止uwsgi
cmd=/opt/ops/ops_python3/bin/uwsgi
if [ -e ${pid_file} ];then
    ${cmd} --stop ${pid_file}
    rm -rf ${pid_file}
    sleep 1
    echo "OK."
fi

# 停止告警查询定时器
service ops_warning_timer stop

# 停止告会议质量计算定时器
service ops_quality_timer stop

# 防止残留进程
ops_pid="$(pidof ops)"
if [ -z "${ops_pid}" ];then
    ops_pid="$(pidof ops-master)"
else
    ops_pid="${ops_pid} $(pidof ops-master)"
fi
[ -z "${ops_pid}" ] && echo "ops is already stoped" || kill -9 ${ops_pid}

# 删除日报定时任务
root_cron_rule_file=/var/spool/cron/root
script=/opt/ops/ops_server/platreport/cron_generate_report_script.py
grep -q "${script}" ${root_cron_rule_file} &&{
    sed -i "\/opt\/ops\/ops_server\/platreport\/cron_generate_report_script.py/d"  /var/spool/cron/root
}||{
    echo "${script} cron has been delete."
}

# 停止资源采集器
if [ -z "$(pidof resource_watcher)" ]; then
    echo -e "$(date)\nresource_watcher is not running..."
else
    kill -9 $(pidof resource_watcher)
fi
