#!/bin/bash
kdf=/opt/data/luban/shells
. $kdf/kdfunctions
ssh_port=22223
ip_info=$1
log_path=$2
path=$3
pas=`cat $ip_info |grep pas |cut -d '=' -f 2`
pas=($pas)
num=${#pas[@]} 
if [ $num == 0 ]; then
    echo  -e "\e[1;31m Error:获取pas的IP失败！\e[0m" 
    exit 
fi
for pasvar in ${pas[@]};
do
    port=$(ssh -o StrictHostKeyChecking=no -p 33332 root@$pasvar netstat -tnlp | grep pas | awk '{print $4}' | awk -F":" '{print $2}' | sort -n | head -1)
	echo -e "\n"|telnet $pasvar ${port} 2>/dev/null | grep -q Connected
	if [ "$?" == "0" ];then
		function_pas(){	
			/usr/bin/expect << EOF
			spawn telnet $pasvar ${port}
			expect "Username:"
			send "\r"
			expect "Password:"
			send "\r"
			expect "pas->"
			send "showbrdstatus\r"
			expect "pas->"
			send "showmoduleinfo\r"
			expect "pas->"
			send "bye\r"
EOF
		}
		function_pas > $log_path/pas_"$pasvar".log
        set_field_value $path pas_$pasvar ip $pasvar
		cat $log_path/pas_"$pasvar".log |grep "SBS state: Running" &>     /dev/null 
		if [ "$?" == 0 ];then
			status=0
			set_field_value $path pas_$pasvar status $status
		else
			status=1
			set_field_value $path pas_$pasvar status $status
			err_info="pas check status fail"
			check_method="telnet "$pasvar" ${port};send showbrdstatus"
			echo "err_info="$err_info"" >> $path
        	echo "check_method="$check_method""    >> $path
		fi

	else
		status=1
		set_field_value $path pas_$pasvar status $status
		err_info="no pas process"
        check_method="telnet "$pasvar" ${port}"
        echo "err_info="$err_info"" >> $path
        echo "check_method="$check_method""    >> $path
	fi
done