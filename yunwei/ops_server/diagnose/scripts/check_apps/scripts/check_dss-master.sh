#!/bin/bash
kdf=/opt/data/luban/shells
. $kdf/kdfunctions
ssh_port=22223
ip_info=$1
log_path=$2
path=$3
dss_m=`cat $ip_info |grep "dss-master" |cut -d '=' -f 2`
dss_m=($dss_m)
num=${#dss_m[@]} 
if [ $num == 0 ]; then
    echo  -e "\e[1;31m Error:获取dss_m的IP失败！\e[0m" 
    exit 
fi
for dss_mvar in ${dss_m[@]};
do
    port=$(ssh -o StrictHostKeyChecking=no -p 33332 root@$dss_mvar netstat -tnlp | grep dssmaster | awk '{print $4}' | awk -F":" '{print $2}' | sort -n | head -1)
    echo -e "\n"|telnet $dss_mvar ${port} 2>/dev/null | grep -q Connected
	if [ "$?" == "0" ];then
		function_dss_m(){	
			/usr/bin/expect << EOF
			spawn telnet $dss_mvar ${port}
			expect "Username:"
			send "\r"
			expect "Password:"
			send "\r"
			expect "dssmaster->"
			send "showworker\r"
			expect "dssmaster->"
			send "showzk\r"
			expect "dssmaster->"
			send "showrmq\r"
			expect "dssmaster->"
			send "bye\r"
EOF
		}
		function_dss_m > $log_path/dss_m_"$dss_mvar".log
		###主从状态######
        cat $log_path/dss_m_"$dss_mvar".log |grep  Zk|grep "LockState<3>" &>     /dev/null 
        if [ "$?" == 0 ];then
            master_slave=master
        else
            master_slave=slave
        fi
        set_field_value $path dss_m_$dss_mvar ip $dss_mvar
        set_field_value $path dss_m_$dss_mvar master_slave $master_slave

		if [ "$master_slave" == "master" ];then
			cat $log_path/dss_m_"$dss_mvar".log |grep  Rmq|grep "IsConnect.1" &>     /dev/null 
			if [ "$?" == 0 ];then
				status=0
				flag=0
				set_field_value $path dss_m_$dss_mvar status $status
			else
				status=1
				set_field_value $path dss_m_$dss_mvar status $status
				err_info="dss_m Connected Rmq fail"
				check_method="telnet "$dss_mvar" ${port};send showrmq"
				echo "err_info="$err_info"" >> $path
        		echo "check_method="$check_method""    >> $path
        	fi
        	dss_worker_num=`cat $log_path/dss_m_"$dss_mvar".log |grep Worker |grep "IsConnect<Y>" |wc -l`
        	if [ "$dss_worker_num" == 0 ];then
        		status=1
        		set_field_value $path dss_m_$dss_mvar status $status
        		if [ "$flag" == 0 ];then
        			err_info="dss_m has no dss_worker"
					check_method="telnet "$dss_mvar" ${port};send showworker"
					echo "err_info="$err_info"" >> $path
        			echo "check_method="$check_method""    >> $path
        		else
        			err_info_1="dss_m has no dss_worker"
					check_method_1="telnet "$dss_mvar" ${port};send showworker"
					echo "err_info_1="$err_info_1"" >> $path
        			echo "check_method_1="$check_method_1""    >> $path
        		fi

			fi
		else
			status=0
			set_field_value $path dss_m_$dss_mvar status $status
		fi

	else
		status=1
		set_field_value $path dss_m_$dss_mvar status $status
		err_info="no dss_m process"
        check_method="telnet "$dss_mvar" ${port}"
        echo "err_info="$err_info"" >> $path
        echo "check_method="$check_method""    >> $path
	fi
done