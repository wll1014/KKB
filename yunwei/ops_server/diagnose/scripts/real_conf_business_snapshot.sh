#!/bin/bash

# description: 指定会议号码，获取转发、媒体相关信息并抓包
# argv：
conf_e164=$1 # 会议号码
redis_port=${2:-6379} # redis端口 默认7380
redis_passwd=${3:-KedaRedis16} # redis密码
ssh_port=${4:-33332} # 免密登录ssh端口
#######创建日志路径#########
logs_path=${5:-'/opt/data/ops/media/mtinfo/curr_mtinfo'}
run_flag=$6     # 无实际用途  ps检测进程用
redis_host=${7:-127.0.0.1} # redis地址 默认本地
ip_info_path=/opt/data/ops/media/check_apps/conf/ip_info.ini
ssh_cmd="ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30"

# if [ $# -lt 2 ];then
    # echo "必传参数：会议e164号码、终端e164号码"
    # exit 2
# fi


if [ ! -d "$logs_path" ]; then
  	mkdir -p "$logs_path"
else
	rm -rf $logs_path/*
fi


########检测redis的连通性，连接失败直接退出###########
redis_connect="/usr/sbin/redis-cli -h $redis_host -p $redis_port -a $redis_passwd"
connectted_status=`$redis_connect -r 4 ping`
echo $connectted_status | grep "PONG" &>/dev/null
if [ "$?" == 0 ]; then
	status=ok
else
	echo "$(date) $redis_host redis 连接失败"  >> $logs_path/mtinfo.log
	exit 3
fi
	# confs=`/usr/sbin/redis-cli -h $redisip -p $redis_port -a $redis_passwd SMEMBERS confs`
	# echo $confs |grep $1 &>/dev/null
	# if [ "$?" == 0 ]; then
	# 	redis_host=$redisip
	# fi

redis_connect="/usr/sbin/redis-cli -h $redis_host -p $redis_port -a $redis_passwd"
#echo $conf_e164 $mt_e164 $redis_host $redis_port $redis_passwd $ssh_port $tcpdump_timeout


########获取UPU注册信息############
upu_ip=`cat $ip_info_path |grep "upu "|awk '{print $3}'`

${ssh_cmd} -p $ssh_port root@$upu_ip "/opt/mcu/upu/bin/upu listmt" > $logs_path/upu_10.23.46.33.log



#########获取会议ip地址信息##############
conf_cmu_ip=`$redis_connect hget confex/${conf_e164}  cmu`


if [ "$conf_cmu_ip" = "" ]; then
	echo "$(date) 获取会议占用的cmu_ip失败，请确认会议是否存在"  >> $logs_path/mtinfo.log
	exit 4
fi

# telnet获取cmu信息
cmu_conf_info()
{
	/usr/bin/expect <<-EOF
	spawn telnet $conf_cmu_ip 2551
	expect "Username:"
	send "\r"
	expect "Password:"
	send "\r"
	expect "cmu->"
	send "mculogflush\r"
	expect "cmu->"
	send "bye\r"
	EOF
}
cmu_conf_info  > $logs_path/cmu_mculogflush_info.log

ConfIdx=`cat $logs_path/cmu_mculogflush_info.log |grep "EqpAliasTree"|grep "$conf_e164"|uniq |awk -F. '{print $2}' |cut -d "," -f 1`

conf_info()
{
	/usr/bin/expect <<-EOF
	spawn telnet $conf_cmu_ip 2551
	expect "Username:"
	send "\r"
	expect "Password:"
	send "\r"
	expect "cmu->"
	send "showconfmt $ConfIdx\r"
	expect "cmu->"
	send "showconfall $ConfIdx\r"
	expect "cmu->"
	send "ssw $ConfIdx\r"
	expect "cmu->"
	send "scs $ConfIdx\r"
	expect "cmu->"
	send "showmix\r"
	expect "cmu->"
	send "showallvmp\r"
	expect "cmu->"
	send "showmtstat $ConfIdx\r"
	expect "cmu->"
	send "bye\r"
	EOF
}
conf_info > $logs_path/cmu_show_info.log


#########获取mpu信息##############
mpu_str=`$redis_connect  keys media/Rack/* |grep "${conf_e164}"`
if [ ! -n "$mpu_str" ];then
	echo "$(date) 未查询到会议占用的媒体ip，请确认！"  >> $logs_path/mtinfo.log
else
	mpu_moid=`echo $mpu_str |awk -F"/" '{print $3}'`
	mpu_ip=`$redis_connect hget  media/Rack/$mpu_moid IpAddr`
	mpu_type=`$redis_connect hget  media/Rack/$mpu_moid RackType`
	mpu_flag=0
fi

###########确定会议占用的mpuip#########

if [ "$mpu_flag" == "0" ];then
	if [ "$mpu_type" == "MPS" ];then
		mpuagent_port=`${ssh_cmd} -p $ssh_port root@$mpu_ip "netstat -nlp |grep mpuagent|grep tcp |grep "0.0.0.0:25" 2>/dev/null |awk -F":" '{print $2}'|awk '{print $1}'`
		mpuagent_info()
	{
		/usr/bin/expect <<-EOF
		spawn telnet $mpu_ip $mpuagent_port
		expect "Username:"
		send "\r"
		expect "Password:"
		send "\r"
		expect "MpuAgent->"
		send "showmc\r"
		expect "================================"
		send "\r"
		expect "MpuAgent->"
		send "bye\r"
		EOF
	}
		mpuagent_info > $logs_path/mpuagent_info.log
		MPU_port=`cat $logs_path/mpuagent_info.log |grep  E164:${conf_e164} -A 1 |grep " MpuPort:"|awk -F":" '{print $3}'|cut -d '-' -f 1`
		MPU_telnet_port=`cat $logs_path/mpuagent_info.log |grep  E164:${conf_e164} -A 1 |grep " MpuPort:"|awk -F":" '{print $4}'|awk  '{print $1}'`
		mpu_info()
	{
		/usr/bin/expect <<-EOF
		spawn telnet $mpu_ip $MPU_telnet_port
		expect "Username:"
		send "\r"
		expect "Password:"
		send "\r"
		expect "mpu_*->"
		send "showallvmp\r"
		expect "mpu_*->"
		send "mpumix\r"
		expect "mpu_*->"
		send "mpuvbas\r"
		expect "mpu_*->"
		send "mpuabas\r"
		expect "mpu_*->"
		send "bye\r"
		EOF
	}
		mpu_info > $logs_path/mpu_info.log
	else
		echo -e "$(date) $mpu_ip 非x86服务器，请手动抓包"  >> $logs_path/mtinfo.log
	fi
fi

#########获取dssinfo信息##############
dss_ips=`cat $ip_info_path |grep dss |cut -d '=' -f 2`
# dss_ips="10.23.46.120 10.23.46.55 10.23.46.39 10.23.46.40 47.100.234.199 47.100.207.123 101.133.222.151 101.133.231.144"
callmanager_ips=`cat $ip_info_path |grep aps |cut -d '=' -f 2`
# callmanager_ips="10.23.46.120 10.23.46.55 10.23.46.39 10.23.46.40 47.100.192.155 106.14.151.0"
dssinfo()
{
	/usr/bin/expect <<-EOF
	spawn telnet $i $dssworkerport
	expect "Username:"
	send "\r"
	expect "Password:"
	send "\r"
	expect "dssworker->"
	send "dsinfo\r"
	expect "dssworker->"
	send "showrtp\r"
	sleep 5
	expect "dssworker->"
	send "dsinfo\r"
	expect "dssworker->"
	send "bye\r"
	EOF
}
callmanagerinfo()
{
	/usr/bin/expect <<-EOF
	spawn telnet $j $callmanagerport
	expect "Username:"
	send "\r"
	expect "Password:"
	send "\r"
	expect "PAS_CM->"
	send "ssw\r"
	expect "PAS_CM->"
	send "showcallinfo\r"
	expect "PAS_CM->"
	send "bye\r"
	EOF
}
for i in $dss_ips;
do
	dssworkerport=`${ssh_cmd} -p $ssh_port root@$i "netstat -nlp |grep dssworker|grep tcp |grep "0.0.0.0:2"" 2>/dev/null |awk -F":" '{print $2}'|awk '{print $1}'`
	dssinfo  > $logs_path/dss_${i}.log
done
for j in $callmanager_ips;
do
	callmanagerport=`${ssh_cmd} -p $ssh_port root@$j "netstat -nlp |grep callmanager|grep tcp |grep "0.0.0.0:2"" 2>/dev/null |awk -F":" '{print $2}'|awk '{print $1}'`
	callmanagerinfo > $logs_path/callmanager_${j}.log
done

cat>$logs_path/conf_info.txt<<EOF
[conf_info]
####cmu_ip######
cmuip=$conf_cmu_ip
#媒体信息#
mpu_ip=$mpu_ip
MPU_port=$MPU_port
telnet_port=$MPU_telnet_port
EOF


