#!/usr/bin/env bash
# 后台自动检测导出进程，并在导出结束后自动更新数据库

if [ $# -ne 5 ]; then
    echo "参数错误，task_id:$1 mysql_user:$2 mysql_pass:$3 mysql_addr:$4 mysql_port:$5"
    exit 1
fi

task_id=$1
mysql_user=$2
mysql_pass=$3
mysql_addr=$4
mysql_port=$5

log_path=/opt/log/ops/scripts/check_dump.log
if [ ! -d ${log_path} ];then
    mkdir -p $(dirname ${log_path})
fi


function main(){

    my_cli='/opt/midware/mysql/bin/mysql'
    database='ops'

    snapshot_file_path='/opt/data/ops/media/snapshot/'


    # 获取pid
    dump_pids=$(${my_cli} -u${mysql_user} -p${mysql_pass} -h${mysql_addr} -P${mysql_port} ${database} -e "select pids from snapshot_task where id=\"${task_id}\"" 2>/dev/null)
    pids=${dump_pids//pids/}
    pids_arr=(${pids//;/ })


    # 查询pid是否运行结束
    for pid in ${pids_arr[@]};do
        while :;do
            ps -ef | grep "${pid}" | grep "elasticdump" | grep -v "grep"
            if [ $? -ne 0 ];then
                break
            fi
        sleep 1
        done
    done


    filename=$(${my_cli} -u${mysql_user} -p${mysql_pass} -h${mysql_addr} -P${mysql_port} ${database} -e "select filename from snapshot_task where id=${task_id}" 2>/dev/null)
    cd ${snapshot_file_path}
    filename=${filename//filename/}
    err_msg=$(tar -zcf ${filename} ${filename//.tar.gz/} 2>&1)
    if [ $? -ne 0 ];then
        ${my_cli} -u${mysql_user} -p${mysql_pass} -h${mysql_addr} -P${mysql_port} ${database} -e "update snapshot_task set is_complete=\"2\",err_msg=\"${err_msg}\" where id=\"${task_id}\""
        return
    fi

    filesize=$(ls -l ${filename} | awk '{ print $5 }')
    filemd5=$(md5sum ${filename} | awk '{ print $1 }')

    ${my_cli} -u${mysql_user} -p${mysql_pass} -h${mysql_addr} -P${mysql_port} ${database} -e "update snapshot_task set filesize=\"${filesize}\",md5=\"${filemd5}\",is_complete=\"1\" where id=\"${task_id}\""
}

main >${log_path} 2>&1 &

