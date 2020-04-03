#!/bin/bash
kdf=/opt/data/luban/shells
. $kdf/kdfunctions
ssh_port=22223
ip_info=$1
log_path=$2
path=$3
mediamaster=`cat $ip_info |grep "media-master" |cut -d '=' -f 2`
mediamaster=($mediamaster)
num=${#mediamaster[@]} 
if [ $num == 0 ]; then
    echo  -e "\e[1;31m Error:获取mediamaster的IP失败！\e[0m" 
    exit 
fi
for mediamastervar in ${mediamaster[@]};
do
    port=$(ssh -o StrictHostKeyChecking=no -p 33332 root@$mediamastervar netstat -tnlp | grep mediamaster | awk '{print $4}' | awk -F":" '{print $2}')
    echo -e "\n"|telnet $mediamastervar ${port} 2>/dev/null | grep -q Connected
    echo "[mediamastervar_$mediamastervar]" >> $path
	if [ "$?" == "0" ];then
		function_mediamaster(){
			/usr/bin/expect << EOF
			spawn telnet $mediamastervar ${port}
			expect "Username:"
			send "\r"
			expect "Password:"
			send "\r"
			expect "mediamaster->"
			send "showcfg\r"
			expect "mediamaster->"
			send "showmw\r"
			expect "mediamaster->"
			send "showmqhbinfo\r"
			expect "mediamaster->"
			send "bye\r"
EOF
		}
		function_mediamaster > $log_path/mediamastervar_"$mediamastervar".log

		cat $log_path/mediamastervar_"$mediamastervar".log  | grep "IsMain:         1" &>     /dev/null 
		if [ "$?" == 0 ];then
            master_slave=master
        else
            master_slave=slave
        fi
        set_field_value $path mediamastervar_$mediamastervar ip $mediamastervar
		set_field_value $path mediamastervar_$mediamastervar master_slave $master_slave
		if [ "$master_slave" == "master" ];then
			cat $log_path/mediamastervar_"$mediamastervar".log  | grep "MediaRes BrdNum" &>     /dev/null 
			if [ "$?" == 0 ];then
				status=0
				flag=0
				set_field_value $path mediamastervar_$mediamastervar status $status
        	else
        		status=1
                set_field_value $path mediamastervar_$mediamastervar status $status
        		err_info="mediamastervar has no mediares"
        		check_method="telnet $mediamastervar ${port};send showmw"
        		echo "err_info=$err_info" >> $path
        		echo "check_method="$check_method""    >> $path
        	fi
        	rmq_rcv_num=`cat $log_path/mediamastervar_"$mediamastervar".log  | grep "RmtRK:mw.mmmw.k:"|wc -l`
        	rmq_status_num=`cat $log_path/mediamastervar_"$mediamastervar".log  | grep "Connect Status: normal"|wc -l`
        	if [ "$rmq_rcv_num" == "$rmq_status_num" ];then
        		status=0
        		set_field_value $path mediamastervar_$mediamastervar status $status
        	else
        		if [ "$flag" == 0 ];then
        			status=1
        			set_field_value $path mediamastervar_$mediamastervar status $status
        			err_info="mediamastervar Connect rabbitmq fail"
        			check_method="telnet "$mediamastervar" ${port};send showmqhbinfo"
        			echo "err_info="$err_info"" >> $path
        			echo "check_method="$check_method""    >> $path
        		else
        			status=1
        			set_field_value $path mediamastervar_$mediamastervar status $status
        			err_info_1="mediamastervar Connect rabbitmq fail"
        			check_method_1="telnet "$mediamastervar" ${port};send showmqhbinfo"
        			echo "err_info_1="$err_info_1"" >> $path
        			echo "check_method_1="$check_method_1""    >> $path
        		fi
        	fi
		else
			status=0
			set_field_value $path mediamastervar_$mediamastervar status $status

		fi
	else
		status=1
		err_info="no mediamastervar process"
        check_method="telnet "$mediamastervar" ${port}"
        set_field_value $path mediamastervar_$mediamastervar ip $mediamastervar
        set_field_value $path mediamastervar_$mediamastervar status $status
        echo "err_info="$err_info"" >> $path
        echo "check_method="$check_method""    >> $path
	fi
done
