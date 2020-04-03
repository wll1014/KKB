#!/bin/bash

base_path=/opt/ops/ops_server/diagnose/scripts/app_check
scripts_path=${base_path}/scripts
echo > ${base_path}/status.ini
rm -rf${base_path}/log/*

$scripts_path/check_aps.sh
$scripts_path/check_callmanager.sh
$scripts_path/check_cmdataproxy.sh
$scripts_path/check_cmu.sh
$scripts_path/check_css.sh
$scripts_path/check_dss_m.sh
$scripts_path/check_ejabberd.sh
$scripts_path/check_gfs.sh
$scripts_path/check_gk.sh
$scripts_path/check_mediamaster.sh
$scripts_path/check_modbcore.sh
$scripts_path/check_modb.sh
$scripts_path/check_mysql.sh
$scripts_path/check_ngi.sh
$scripts_path/check_pas.sh
$scripts_path/check_rabbitmq.sh
$scripts_path/check_redis.sh
$scripts_path/check_rms.sh
$scripts_path/check_upucore.sh
$scripts_path/check_upu.sh
$scripts_path/check_web.sh
$scripts_path/check_zk.sh
