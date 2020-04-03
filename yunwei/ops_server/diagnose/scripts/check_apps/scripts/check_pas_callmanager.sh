#!/bin/bash
kdf=/opt/data/luban/shells
. $kdf/kdfunctions
ssh_port=22223
ip_info=$1
log_path=$2
path=$3
callmanager=`cat $ip_info |grep pas |cut -d '=' -f 2`
callmanager=($callmanager)
num=${#callmanager[@]} 
if [ $num == 0 ]; then
    echo  -e "\e[1;31m Error:获取callmanager的IP失败！\e[0m" 
    exit 
fi
for callmanagervar in ${callmanager[@]};
do
    port=$(ssh -o StrictHostKeyChecking=no -p 33332 root@$callmanagervar netstat -tnlp | grep callmanager | awk '{print $4}' | awk -F":" '{print $2}' | sort -n | head -1)
    echo -e "\n"|telnet $callmanagervar ${port} 2>/dev/null | grep -q Connected
	if [ "$?" == "0" ];then
		function_callmanager(){	
			/usr/bin/expect << EOF
			spawn telnet $callmanagervar ${port}
			expect "Username:"
			send "\r"
			expect "Password:"
			send "\r"
			expect "callmanager->"
			send "showc\r"
			expect "callmanager->"
			send "showp\r"
			expect "callmanager->"
			send "showcmstatus\r"
			expect "callmanager->"			
			send "bye\r"
EOF
		}
		function_callmanager > $log_path/callmanager_"$callmanagervar".log
        set_field_value $path callmanager_$callmanagervar ip $callmanagervar
		cat $log_path/callmanager_"$callmanagervar".log |grep "status: except" &>     /dev/null 
		if [ "$?" == 0 ];then
			flag=1
			status=1
			set_field_value $path callmanager_$callmanagervar status $status
			err_info="callmanager Connected rabbitmq fail"
			check_method="telnet "$callmanagervar" ${port};send showc showp"
			echo "err_info="$err_info"" >> $path
        	echo "check_method="$check_method""    >> $path

		else
			status=0
			set_field_value $path callmanager_$callmanagervar status $status
		fi
		cat $log_path/callmanager_"$callmanagervar".log |grep "RmsClient status: 1" &>     /dev/null 
		if [ "$?" != 0 ];then
			RmsClient_status=down
		fi
		cat $log_path/callmanager_"$callmanagervar".log |grep -e "emDssStatus_ResourceOnline" -e "emDssStatus_InitStatusSuccess" &>     /dev/null
		if [ "$?" != 0 ];then
			DssStatus=down
		fi 
		cat $log_path/callmanager_"$callmanagervar".log |grep "UpuConnectState:1" &>     /dev/null
		if [ "$?" != 0 ];then
			UpuConnectState=down
		fi 
		if [ "$RmsClient_status" == "down" ]||[ "$DssStatus" == "down" ]||[ "$UpuConnectState" == "down" ];then
			status=1
			set_field_value $path callmanager_$callmanagervar status $status
			if [ "$flag" == 1 ];then
				err_info_1="callmanager status error"
        		check_method_1="telnet "$callmanagervar" ${port};send showcmstatus"
        		echo "err_info_1="$err_info_1"" >> $path
        		echo "check_method_1="$check_method_1""    >> $path
			else
				err_info="callmanager status error"
        		check_method="telnet "$callmanagervar" ${port};send showcmstatus"
        		echo "err_info="$err_info"" >> $path
        		echo "check_method="$check_method""    >> $path
			fi
		fi
	else
		status=1
		set_field_value $path callmanager_$callmanagervar status $status
		err_info="no callmanager process"
        check_method="telnet "$callmanagervar" ${port}"
        echo "err_info="$err_info"" >> $path
        echo "check_method="$check_method""    >> $path
	fi
done