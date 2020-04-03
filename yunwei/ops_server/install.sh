#!/bin/bash -x

PS4="$(date) +"
cur_dir=$(cd $(dirname $0);pwd)
pip3_cmd=/opt/midware/python3/bin/pip3
python3_cmd=/opt/midware/python3/bin/python3
package_dir=/opt/ops/ops_server/build/requirement_package
requirement_path=/opt/ops/ops_server/requirements.txt
uwsgi_ini_path=/opt/ops/ops_server/uwsgi.ini
ops_manage=/opt/ops/ops_server/manage.py
lib_path=/opt/ops/ops_python3/
mysql_username=kedacom
mysql_password=KedaMysql16#
mysql_db=ops
# flag接收第一个传参，默认0：正常安装; 1：不执行安装操作，执行清空数据库，并执行migrate
flag=${1:-0}
cd ${cur_dir}

function custom_scripts_install() {
    # 自定义脚本服务安装
    mkdir -p /opt/data/ops/media/custom_scripts/conf/
    mkdir -p /opt/data/ops/media/custom_scripts/scripts/
    \cp ./custom_scripts_timer/ops_custom_scripts_timer /etc/init.d/
    # 软连接到环境变量目录
    ln -sf /opt/ops/ops_server/custom_scripts_timer/ops_get.py /usr/bin/ops_get
    # 复制示例文件
    \cp ./custom_scripts_timer/example/is-* /opt/data/ops/media/custom_scripts/conf/
    \cp ./custom_scripts_timer/example/*.conf /opt/data/ops/media/custom_scripts/conf/
    \cp ./custom_scripts_timer/example/*.sh /opt/data/ops/media/custom_scripts/scripts/
}

function install() {
    # 告警定时器启动脚本
    \cp ./warning_timer/ops_warning_timer /etc/init.d/
    # 会议质量定时器启动脚本
    \cp ./qualitytimer/ops_quality_timer /etc/init.d/
    custom_scripts_install
    cd ./build/requirement_package

    # 安装依赖包
    ${pip3_cmd} install  --no-index   --find-links=${package_dir}  -r  ${requirement_path} --prefix=${lib_path}

    # 按cpu核数设置uwsgi启动进程个数
    cpu_processor_num=$(cat /proc/cpuinfo | grep processor | wc -l)
    sed -i 's/workers.*/workers='${cpu_processor_num}'/' ${uwsgi_ini_path}
}

function start_mysqld() {
    retry_count=5
    for (( i = 0; i < ${retry_count}; i++ )); do
        service mysqld status
        ret=$?
        if [ ${ret} -eq 0 ]; then
            break
        else
            echo "$(date) mysqld is not running..."
            service mysqld start
            sleep 1
        fi
    done
    return ${ret}
}

function clear_ops_database() {
    database=ops
    sql="drop database if exists ${database};create database if not exists ${database} default charset utf8;"
    mysql -u${mysql_username} -p${mysql_password} -e "${sql}"
}

function ops_migrate() {
    export PYTHONPATH=${PYTHONPATH}:/opt/ops/ops_python3/lib/python3.5/site-packages/
    # 数据库迁移
    ${python3_cmd} ${ops_manage} makemigrations
    ${python3_cmd} ${ops_manage} migrate
    # 导航栏默认数据
    mysql -u${mysql_username} -p${mysql_password} ${mysql_db} -e "TRUNCATE sidebar;"
    ${python3_cmd} ${ops_manage} loaddata $(dirname ${ops_manage})/sidebar/sidebar.json
    # 告警码默认数据
    mysql -u${mysql_username} -p${mysql_password} ${mysql_db} -e "TRUNCATE warning_code;"
    ${python3_cmd} ${ops_manage} loaddata $(dirname ${ops_manage})/warning/warning_codes.json
    # 省市默认数据
    ${python3_cmd} ${ops_manage} loaddata $(dirname ${ops_manage})/overview/province.json
    ${python3_cmd} ${ops_manage} loaddata  $(dirname ${ops_manage})/overview/city.json
    # 告警阈值默认数据
	warning_threshold_count=$(mysql -u${mysql_username} -p${mysql_password} ${mysql_db} -e "select count(*) from warning_threshold")
	warning_threshold_count=$(echo ${warning_threshold_count} | awk '{print $2}')
	if [ x"${warning_threshold_count}" != x1 ];then
	    ${python3_cmd} ${ops_manage} loaddata $(dirname ${ops_manage})/warning/warning_threshold.json
	fi
    # 自定义抓包任务默认数据
    custom_capture_task_count=$(mysql -u${mysql_username} -p${mysql_password} ${mysql_db} -e "select count(*) from custom_capture_task")
	custom_capture_task_count=$(echo ${custom_capture_task_count} | awk '{print $2}')
    if [ x"${custom_capture_task_count}" != x1 ];then
        default_start_time=$[$(date +"%s") * 1000]
        default_timeout=30
        mysql -u${mysql_username} -p${mysql_password} ${mysql_db} -e "TRUNCATE custom_capture_task;
        INSERT INTO custom_capture_task (start_time, timeout) VALUES (${default_start_time}, ${default_timeout});"
    fi

      # faq 用户数据备份
      mysqldump -u${mysql_username} -p${mysql_password} --no-create-db=TRUE --no-create-info=TRUE --add-drop-table=FALSE -E -R --set-gtid-purged=off --where="id>999" ops faq_classifications > faq_classifications.sql
      mysqldump -u${mysql_username} -p${mysql_password} --no-create-db=TRUE --no-create-info=TRUE --add-drop-table=FALSE -E -R --set-gtid-purged=off --where="record_id>9999" ops faq_records > faq_records.sql
      mysql -u${mysql_username} -p${mysql_password} ${mysql_db} -e "TRUNCATE faq_records;"
      mysql -u${mysql_username} -p${mysql_password} ${mysql_db} -e "SET FOREIGN_KEY_CHECKS=0;TRUNCATE faq_classifications;SET FOREIGN_KEY_CHECKS=1;"
      ${python3_cmd} ${ops_manage} loaddata $(dirname ${ops_manage})/faq/faq.json
      mysql -u${mysql_username} -p${mysql_password} ${mysql_db} < faq_classifications.sql
      mysql -u${mysql_username} -p${mysql_password} ${mysql_db} < faq_records.sql
  }

function normal_setup() {
    # 正常安装
    install
    start_mysqld
    ret=$?
    if [ ${ret} -eq 0 ]; then
        ops_migrate
    else
        echo "$(date) mysqld is not running...exit..."
        exit 1
    fi
}

function restore_database() {
    # 不执行安装操作，执行清空数据库，并进行ops的Django migrate
    start_mysqld
    ret=$?
    if [ ${ret} -eq 0 ]; then
        clear_ops_database
        ops_migrate
    else
        echo "$(date) mysqld is not running...exit..."
        exit 1
    fi
}

if [ ${flag} -eq 1 ]; then
    # 清空数据使用
    restore_database
else
    # 正常安装使用
    normal_setup
fi

exit $?
