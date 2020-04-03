#!/usr/bin/env bash

path=$(cd $(dirname $0);pwd)
cmd=/opt/ops/ops_python3/bin/uwsgi

# 启动uwsgi
${cmd} --ini ${path}/uwsgi.ini

# 启动告警查询定时器
service ops_warning_timer restart

# 启动会议质量计算定时器
service ops_quality_timer restart

# 启动自定义脚本执行定时器
service ops_custom_scripts_timer restart

# 添加日报定时任务
cron_rule='1 0 * * *'
root_cron_rule_file=/var/spool/cron/root
script=/opt/ops/ops_server/platreport/cron_generate_report_script.py
resourcewatcher=/opt/ops/ops_server/resourcewatcher/resource_watcher.py
pythonpath=/opt/ops/ops_python3/lib/python3.5/site-packages/
python3=/opt/midware/python3/bin/python3
log_path=/opt/log/ops/ops_info.log
grep -q "${script}" ${root_cron_rule_file} &&{
    echo "${script} cron has been setted."
}||{
    echo "${cron_rule} PYTHONPATH=${pythonpath} ${python3} ${script} >> ${log_path} 2>&1" >> ${root_cron_rule_file}
}

# 启动媒体资源采集器
if [ -z $(pidof resource_watcher) ]; then
    PYTHONPATH=${pythonpath} ${python3} ${resourcewatcher} 2>&1 > /dev/null &
fi
