#!/bin/bash
kdf=/opt/data/luban/shells
. $kdf/kdfunctions
ssh_port=22223
ip_info=$1
log_path=$2
path=$3
ngi=`cat $ip_info |grep pas |cut -d '=' -f 2`
ngi=($ngi)
num=${#ngi[@]} 
if [ $num == 0 ]; then
    echo  -e "\e[1;31m Error:获取ngi的IP失败！\e[0m" 
    exit 
fi
for ngivar in ${ngi[@]};
do
    port=$(ssh -o StrictHostKeyChecking=no -p 33332 root@$ngivar netstat -tnlp | grep -w ngi | awk '{print $4}' | awk -F":" '{print $2}' | sort -n | head -1)
    echo -e "\n"|telnet $ngivar ${port} 2>/dev/null | grep -q Connected
	if [ "$?" == "0" ];then
		function_ngi(){	
			/usr/bin/expect << EOF
			spawn telnet $ngivar ${port}
			expect "Username:"
			send "\r"
			expect "ngisword:"
			send "\r"
			expect "ngi->"
			send "showc\r"
			expect "ngi->"
			send "showp\r"
			expect "ngi->"
			send "bye\r"
EOF
		}
		function_ngi > $log_path/ngi_"$ngivar".log
        set_field_value $path ngi_$ngivar ip $ngivar
		cat $log_path/ngi_"$ngivar".log | grep "status: except" &>     /dev/null 
		if [ "$?" == 0 ];then
			status=1
			set_field_value $path ngi_$ngivar status $status
			err_info="ngi Connected rabbitmq fail"
			check_method="telnet "$ngivar" ${port};send showc showp"
			echo "err_info="$err_info"" >> $path
        	echo "check_method="$check_method""    >> $path

		else
			status=0
			set_field_value $path ngi_$ngivar status $status
		fi

	else
		status=1
		set_field_value $path ngi_$ngivar status $status
		err_info="no ngi process"
        check_method="telnet "$ngivar" ${port}"
        echo "err_info="$err_info"" >> $path
        echo "check_method="$check_method""    >> $path
	fi
done
