#!/bin/bash

# description: 指定会议号码、终端号码，获取转发、媒体相关信息并抓包
# argv：
conf_e164=$1 # 会议号码
mt_e164=$2 # 终端号码
redis_host=${3:-127.0.0.1} # redis地址 默认本地
redis_port=${4:-7380} # redis端口 默认7380
redis_passwd=${5:-KedaRedis16} # redis密码
ssh_port=${6:-33332} # 免密登录ssh端口
tcpdump_timeout=${7:-30} # 抓包持续时间 默认30s

if [ $# -lt 2 ];then
    echo "必传参数：会议e164号码、终端e164号码"
    exit 2
fi

#echo $conf_e164 $mt_e164 $redis_host $redis_port $redis_passwd $ssh_port $tcpdump_timeout

logs_path=/opt/data/ops/media/mtinfo/curr_mtinfo

if [ ! -d "$logs_path" ]; then
  	mkdir -p "$logs_path"
else
	rm -rf $logs_path/*
fi
redis_connect="/usr/sbin/redis-cli -h $redis_host -p $redis_port -a $redis_passwd"
ssh_cmd="ssh -o StrictHostKeyChecking=no "
scp_cmd="scp -o StrictHostKeyChecking=no "
########检测redis的连通性，连接失败直接退出###########
connectted_status=`$redis_connect -r 4 ping`
echo $connectted_status | grep "PONG" &>/dev/null
if [ "$?" == 0 ]; then
	status=ok
else
	echo "$(date) $redis_host redis 连接失败"  >> $logs_path/mtinfo.log
	exit 3
fi
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
	send "mculogflush \r"
	expect "cmu->"
	send "bye\r"
	EOF
}
cmu_conf_info  > $logs_path/cmu_conf_info.log
ConfIdx=`cat $logs_path/cmu_conf_info.log |grep "EqpAliasTree"|grep "$conf_e164"|uniq |awk -F. '{print $2}' |cut -d "," -f 1`

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
#########获取mt_port信息##############
mt_id=`$redis_connect hget conf/${conf_e164}/e164tomtid ${mt_e164}`
jion_conf_status=`$redis_connect hget conf/${conf_e164}/mt/$mt_id online`

if [ "$jion_conf_status" == "0" ] || [ -z "$jion_conf_status" ]; then
    # online为0或未取到，则认为终端不在会议
	echo "$(date) $2 未加入会议，请确认" >> $logs_path/mtinfo.log
	exit 5
fi

mt_ip=`$redis_connect hget conf/${conf_e164}/mt/$mt_id mtip`
####平台发送音频端口######
dss_str=`$redis_connect hmget conf/${conf_e164}/mt/$mt_id/arcvchn/1 rtpip rtpport`
dss_ip=`echo $dss_str |awk '{print $1}'`
plat_send_aduio_port=`echo $dss_str |awk '{print $2}'`
####平台发送视频端口######
plat_send_video_port=`$redis_connect hget conf/${conf_e164}/mt/$mt_id/vrcvchn/1 rtpport`
####平台接收音频端口######
plat_rcv_aduio_port=`$redis_connect hget conf/${conf_e164}/mt/$mt_id/asendchn/1 rtpport`
####平台接收视频端口######
plat_rcv_video_port=`$redis_connect hget conf/${conf_e164}/mt/$mt_id/vsendchn/1 rtpport`
######双流端口######
h239_port=`$redis_connect hget conf/${conf_e164}/mt/$mt_id/drcvchn/1 rtpport`

#########获取dssinfo信息##############
dssinfo()
{
	/usr/bin/expect <<-EOF
	spawn telnet $dss_ip 2970
	expect "Username:"
	send "\r"
	expect "Password:"
	send "\r"
	expect "dssworker->"
	send "dsinfo\r"
	expect "dssworker->"
	send "showrtp\r"
	expect "dssworker->"
	send "dsinfo\r"
	expect "dssworker->"
	send "bye\r"
	EOF
}
dssinfo  > $logs_path/dss_info.log

#########获取mpu信息##############
mpu_str=`$redis_connect  keys media/Rack/* |grep "${conf_e164}"`
if [ ! -n "$mpu_str" ] ;then
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
		mpuagent_port=`${ssh_cmd} -p $ssh_port root@$mpu_ip "netstat -nlp |grep mpuagent|grep 250|grep -v udp" 2>/dev/null |awk -F":" '{print $2}'|awk '{print $1}'`
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
#######mtinfo#############
cat>$logs_path/mtinfo.txt<<EOF
[info]
mtip=$mt_ip
dssip=$dss_ip
####平台发送音频端口######
plat_send_aduio_port=$plat_send_aduio_port
####平台发送视频端口######
plat_send_video_port=$plat_send_video_port
####平台接收音频端口######
plat_rcv_aduio_port=$plat_rcv_aduio_port
####平台接收视频端口######
plat_rcv_video_port=$plat_rcv_video_port
#双流端口#
h239_port=$h239_port
#媒体信息#
mpu_ip=$mpu_ip
MPU_port=$MPU_port
telnet_port=$MPU_telnet_port
EOF

# 抓包函数
tcpdump_func(){
    local machine_type=$1
    local ip_addr=$2
    if [ -n "${ip_addr}" ];then
        echo -e "$(date) 开始\"${ip_addr}\"抓包"
        ${ssh_cmd} -p ${ssh_port} root@${ip_addr} " timeout ${tcpdump_timeout}  tcpdump -i any  -s 0 -w /opt/data/${machine_type}_${ip_addr}.pcap "
        echo -e "$(date) 结束\"${ip_addr}\"抓包"
        echo -e "$(date) 开始\"${machine_type}_${ip_addr}.pcap\"传输"
        ${scp_cmd} -P ${ssh_port} root@${ip_addr}:/opt/data/${machine_type}_${ip_addr}.pcap ${logs_path}
        echo -e "$(date) 结束\"${machine_type}_${ip_addr}.pcap\"传输"
    fi
}

tcpdump_func "dss" "${dss_ip}" >> ${logs_path}/mtinfo.log 2>&1 &
tcpdump_func "mpu" "${mpu_ip}" >> ${logs_path}/mtinfo.log 2>&1 &

wait

# 打包抓取的所有信息
v_time=`date "+%Y%m%d%H%M%S"`
cd ${logs_path}/../
tar -czf ${logs_path}/../mtinfo_${mt_e164}_${v_time}.tar.gz ${logs_path##*/} >> ${logs_path}/mtinfo.log 2>&1
ret=$?
cd - >> ${logs_path}/mtinfo.log 2>&1

if [ ${ret} -eq 0 ];then
    # __ops__用于区分其他打印
    echo "__ops__mtinfo_${mt_e164}_${v_time}.tar.gz"
    exit ${ret}
else
    echo "打包失败，return ${ret}, 请查看日志..."
    exit 100
fi
