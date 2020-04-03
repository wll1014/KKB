#!/bin/bash
kdf=/opt/data/luban/shells
. $kdf/kdfunctions
ssh_port=22223
ip_info=$1
log_path=$2
path=$3
cmu=`cat $ip_info |grep cmu |cut -d '=' -f 2`
cmu=($cmu)
num=${#cmu[@]}
if [ $num == 0 ]; then
    echo  -e "\e[1;31m Error:获取cmu的IP失败！\e[0m"
    exit
fi
for cmuvar in ${cmu[@]};
do
    port=$(ssh -o StrictHostKeyChecking=no -p 33332 root@$cmuvar netstat -tnlp | grep cmu | awk '{print $4}' | awk -F":" '{print $2}')
    echo -e "\n"|telnet $cmuvar ${port} 2>/dev/null | grep -q Connected
	if [ "$?" == "0" ];then
		function_cmu(){
			/usr/bin/expect << EOF
			spawn telnet $cmuvar ${port}
			expect "Username:"
			send "\r"
			expect "Password:"
			send "\r"
			expect "cmu->"
			send "checkmcu\r"
			expect "cmu->"
			send "showmtadp\r"
			expect "cmu->"
			send "bye\r"
EOF
		}
		function_cmu  > $log_path/cmu_"$cmuvar".log
		set_field_value $path cmu_$cmuvar ip $cmuvar
		rabbitmq_state=`cat $log_path/cmu_"$cmuvar".log |grep "Producer State.1" |grep "Consumer State.1" |wc -l`
		other_states=`cat $log_path/cmu_"$cmuvar".log |grep "State.1" |grep -v Producer  |wc -l` &>     /dev/null
		upu_state=`cat $log_path/cmu_"$cmuvar".log |grep "OK!" |wc -l`
		if [ "$other_states" -ge 2 ] && [ "$upu_state" == "1" ] && [ "$rabbitmq_state" == "1" ];then
			status=0
			flag=0
			set_field_value $path cmu_$cmuvar status $status
		else
			status=1
			set_field_value $path cmu_$cmuvar status $status
			err_info="cmu check fail"
			check_method="telnet "$cmuvar" ${port};send checkmcu"
			echo "err_info="$err_info"" >> $path
        	echo "check_method="$check_method""    >> $path
		fi
		registed_nu_num=`cat $log_path/cmu_"$cmuvar".log |grep "Register Nu num"|awk '{print $6}'`
		if [ "$registed_nu_num" == 0 ];then
            status=1
            set_field_value $path cmu_$cmuvar status $status
            if [ "$flag" == 0 ];then
            	err_info="no nu registed cmu"
				check_method="telnet "$cmuvar" ${port};send showmtadp"
				echo "err_info="$err_info"" >> $path
        		echo "check_method="$check_method""    >> $path
        	else
        		err_info_1="no nu registed cmu"
				check_method_1="telnet "$cmuvar" ${port};send showmtadp"
				echo "err_info_1="$err_info_1"" >> $path
        		echo "check_method_1="$check_method_1""    >> $path
        	fi
        fi
	else
		status=1
		err_info="no cmu process"
        check_method="telnet "$cmuvar" ${port}"
        set_field_value $path cmu_$cmuvar ip $cmuvar
        set_field_value $path cmu_$cmuvar status $status
        echo "err_info="$err_info"" >> $path
        echo "check_method="$check_method""    >> $path
	fi
done
