#!/bin/bash
kdf=/opt/data/luban/shells
. $kdf/kdfunctions
ssh_port=22223
ip_info=$1
log_path=$2
path=$3
gk=`cat $ip_info |grep pas |cut -d '=' -f 2`
gk=($gk)
num=${#gk[@]} 
if [ $num == 0 ]; then
    echo  -e "\e[1;31m Error:获取gk的IP失败！\e[0m" 
    exit 
fi
for gkvar in ${gk[@]};
do
    port=$(ssh -o StrictHostKeyChecking=no -p 33332 root@$gkvar ss -tnlp | grep gkregistration | awk '{print $4}' | awk -F":" '{print $2}')
    echo -e "\n"|telnet $gkvar ${port} 2>/dev/null | grep -q Connected
	if [ "$?" == "0" ];then
		function_gk(){	
			/usr/bin/expect << EOF
			spawn telnet $gkvar ${port}
			expect "Username:"
			send "\r"
			expect "gksword:"
			send "\r"
			expect "gk->"
			send "status\r"
			expect "gk->"
			send "bye\r"
EOF
		}
		function_gk > $log_path/gk_"$gkvar".log
        set_field_value $path gk_$gkvar ip $gkvar
		cat $log_path/gk_"$gkvar".log |grep "Connect to CM: success" &>     /dev/null 
		if [ "$?" == 0 ];then
			status=0
			set_field_value $path gk_$gkvar status $status
		else
			status=1
			set_field_value $path gk_$gkvar status $status
			err_info="gk Connect to CM fail"
			check_method="telnet "$gkvar" ${port};send status"
			echo "err_info="$err_info"" >> $path
        	echo "check_method="$check_method""    >> $path
		fi

	else
		status=1
		set_field_value $path gk_$gkvar status $status
		err_info="no gk process"
        check_method="telnet "$gkvar" ${port}"
        echo "err_info="$err_info"" >> $path
        echo "check_method="$check_method""    >> $path
	fi
done
