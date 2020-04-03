#!/bin/bash
kdf=/opt/data/luban/shells
. $kdf/kdfunctions
ssh_port=22223
ip_info=$1
log_path=$2
path=$3
rms=`cat $ip_info |grep rms |cut -d '=' -f 2`
rms=($rms)
num=${#rms[@]} 
if [ $num == 0 ]; then
    echo  -e "\e[1;31m Error:获取rms的IP失败！\e[0m" 
    exit 
fi
for rmsvar in ${rms[@]};
do
    port=$(ssh -o StrictHostKeyChecking=no -p 33332 root@$rmsvar netstat -tnlp | grep rms | awk '{print $4}' | awk -F":" '{print $2}')
    echo -e "\n"|telnet $rmsvar ${port} 2>/dev/null | grep -q Connected
	if [ "$?" == "0" ];then
		function_rms(){	
			/usr/bin/expect << EOF
			spawn telnet $rmsvar ${port}
			expect "Username:"
			send "\r"
			expect "Password:"
			send "\r"
			expect "rms->"
			send "check\r"
			expect "rms->"
			send "rms\r"
			expect "rms->"
			send "bye\r"
EOF
		}
		function_rms > $log_path/rms_"$rmsvar".log
		###主从状态######
        cat $log_path/rms_"$rmsvar".log |grep "rms is slave" &>     /dev/null 
        if [ "$?" == 0 ];then
            master_slave=slave
        else
            master_slave=master
        fi
        set_field_value $path rms_$rmsvar ip $rmsvar
        set_field_value $path rms_$rmsvar master_slave $master_slave
		cat $log_path/rms_"$rmsvar".log |grep -P '\Q[fail]\E' &>     /dev/null 
		if [ "$?" == 0 ];then
			status=1
			set_field_value $path rms_$rmsvar status $status
			err_info="rms check fail"
			check_method="telnet "$rmsvar" ${port};send check"
			echo "err_info="$err_info"" >> $path
        	echo "check_method="$check_method""    >> $path
		else
			status=0
			set_field_value $path rms_$rmsvar status $status
		fi

	else
		status=1
		set_field_value $path rms_$rmsvar status $status
		err_info="no rms process"
        check_method="telnet "$rmsvar" ${port}"
        echo "err_info="$err_info"" >> $path
        echo "check_method="$check_method""    >> $path
	fi
done