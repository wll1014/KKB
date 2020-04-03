#!/bin/bash
. /opt/data/luban/shells/kdfunctions
ip_info=$1
rabbitmq_ips=($(grep rabbitmq $ip_info | cut -d"=" -f 2))
# echo ${rabbitmq_ips[@]}
rabbitmq_ha_port=5672
rabbitmq_web_port=5673
log_path=$2
mqinfo=${log_path}/mqinfo.txt
rabbitmqctl=/opt/midware/rabbitmq/server/sbin/rabbitmqctl
old_rabbitmqctl=/opt/midware/rabbitmq/sbin/rabbitmqctl
path=$3


get_ctl()
{
    ip=$1
    ssh -o StrictHostKeyChecking=no -p 33332 root@$ip ls ${rabbitmqctl} 2>/dev/null
    if [ $? -eq 0 ]; then
        echo ${rabbitmqctl}
    else
        echo ${old_rabbitmqctl}
    fi
}

check_link_status()
{
    ip=$1
    echo | telnet $ip $rabbitmq_ha_port  2>/dev/null| grep -q "Connected"
    link_status=$?
    link_err_info="connet 5672 failed"
    link_check_method="telnet $ip $rabbitmq_ha_port"
}

check_web_status()
{
    ip=$1
    web_status=$(curl --connect-timeout 1 --max-time 3 -s -I http://$ip:5673 | grep HTTP | cut -d" " -f 2)
    web_err_info="http://$ip:5673 is not accessible"
    web_check_method="http://$ip:5673"
}

check_cluster_status()
{
    ip=$1
    now_ctl=$2
    rmq_node_num=$(ssh -o StrictHostKeyChecking=no -p 33332 root@$ip ${now_ctl} cluster_status 2>>/dev/null|grep -A2 "disc" |egrep -v "running|cluster"|grep -o "rabbitmq[^]']*"|wc -l)
    cfg_node_num=$(ssh -o StrictHostKeyChecking=no -p 33332 root@$ip cat /opt/data/rabbitmq/cluster_info.ini | grep nodes |cut -d '=' -f2|awk -F ',' '{print NF}')
    rmq_err_info="running nodes is not 2"
    rmq_check_method="${now_ctl} cluster_status"
}


check_queue()
{
    ip=$1
    now_ctl=$2
    n=0
    ssh -o StrictHostKeyChecking=no -p 33332 root@$ip ${now_ctl} list_queues name messages messages_ready messages_unacknowledged consumers | egrep -v "Listing|done|Timeout|name" > $mqinfo
    while read line;do
        mqname=`echo $line|awk '{print $1}'`
        status=(`echo $line | awk '{print $2,$3,$4,$5}'`)
        if [ x"${status[0]}" != x"0" -o x"${status[1]}" != x"0" -o x"${status[2]}" != x"0" ];then
            mq_flag=1
            queue_err_info="$line is not ok"
            queue_check_method="${now_ctl} list_queues name messages messages_ready messages_unacknowledged consumers"
            break
        elif [ x"${status[0]}" == x"0" -a x"${status[1]}" == x"0" -a x"${status[2]}" == x"0" -a x"${status[3]}" == x"0" ];then
            ((n++))
        else
            ((n++))
        fi


    done <$mqinfo
    mq_num=$(cat $mqinfo|wc -l)
    if [ "$n" -eq "$mq_num" -a "$n" -ne 0 ];then
        mq_flag=0
    else
        mq_flag=1
    fi
}

rabbitmq_num=${#rabbitmq_ips[@]}
if [ $rabbitmq_num -eq 2 ];then
    for rabbitmq_ip in ${rabbitmq_ips[@]};do
        ctl=$(get_ctl $rabbitmq_ip)
        echo "[rabbitmq_$rabbitmq_ip]" >> $path
        check_link_status $rabbitmq_ip
        check_web_status $rabbitmq_ip
        check_queue $rabbitmq_ip $ctl
        check_cluster_status $rabbitmq_ip $ctl
        if [[ $link_status -eq 0 && $web_status -eq 200 && $mq_flag -eq 0 && $rmq_node_num -eq $cfg_node_num ]];then
            echo "status = 0" >>$path
            echo "ip = $rabbitmq_ip" >>$path
        elif [ $link_status -ne 0 ];then
            echo "status = 1" >>$path
            echo "ip = $rabbitmq_ip">>$path
            echo "err_info_1 = $link_err_info" >>$path
            echo "check_method_1 = $link_check_method" >>$path
        elif [[ x"$web_status" != x"200" ]];then
            echo "status = 1" >>$path
            echo "ip = $rabbitmq_ip">>$path
            echo "err_info_1 = $web_err_info" >>$path
            echo "check_method_1 = $web_check_method" >>$path
        elif [ $mq_flag -eq 1 ];then
            echo "status = 1" >>$path
            echo "ip = $rabbitmq_ip">>$path
            echo "err_info_1 = $queue_err_info" >>$path
            echo "check_method_1 = $queue_check_method" >>$path
        else
            echo "status = 1" >>$path
            echo "ip = $rabbitmq_ip">>$path
            echo "err_info_1 = $rmq_err_info" >>$path
            echo "check_method_1 = $rmq_check_method" >>$path
        fi
    done
elif [ $rabbitmq_num -ne 0 ];then
    echo "[rabbitmq_$rabbitmq_ips]" >> $path
    ctl=$(get_ctl $rabbitmq_ips)
    check_link_status $rabbitmq_ips
    check_web_status $rabbitmq_ips
    check_queue $rabbitmq_ips $ctl
    if [[ $link_status -eq 0 && $web_status -eq 200 && $mq_flag -eq 0 ]];then
        echo "status = 0" >>$path
        echo "ip = $rabbitmq_ip" >>$path
    elif [ $link_status -ne 0 ];then
        echo "status = 1" >>$path
        echo "ip = $rabbitmq_ip">>$path
        echo "err_info_1 = $link_err_info" >>$path
        echo "check_method_1 = $link_check_method" >>$path
    elif [[ x"$web_status" != x"200" ]];then
        echo "status = 1" >>$path
        echo "ip = $rabbitmq_ip">>$path
        echo "err_info_1 = $web_err_info" >>$path
        echo "check_method_1 = $web_check_method" >>$path
    else
        echo "status = 1" >>$path
        echo "ip = $rabbitmq_ip">>$path
        echo "err_info_1 = $queue_err_info" >>$path
        echo "check_method_1 = $queue_check_method" >>$path
    fi
fi

  
