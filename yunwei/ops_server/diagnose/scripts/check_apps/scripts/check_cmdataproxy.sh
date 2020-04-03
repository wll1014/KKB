#!/bin/bash
kdf=/opt/data/luban/shells
. $kdf/kdfunctions
ssh_port=22223
ip_info=$1
log_path=$2
path=$3
cmdataproxy=`cat $ip_info |grep cmdataproxy |cut -d '=' -f 2`
cmdataproxy=($cmdataproxy)
num=${#cmdataproxy[@]} 
if [ $num == 0 ]; then
    echo  -e "\e[1;31m Error:获取cmdataproxy的IP失败！\e[0m" 
    exit 
fi
for cmdataproxyvar in ${cmdataproxy[@]};
do
    port=$(ssh -o StrictHostKeyChecking=no -p 33332 root@$cmdataproxyvar netstat -tnlp | grep cmdataproxy | awk '{print $4}' | awk -F":" '{print $2}')
    echo -e "\n"|telnet $cmdataproxyvar ${port} 2>/dev/null | grep -q Connected
	if [ "$?" == "0" ];then
		function_cmdataproxy(){
			/usr/bin/expect << EOF
			spawn telnet $cmdataproxyvar ${port}
			expect "Username:"
			send "\r"
			expect "Password:"
			send "\r"
			expect "cmdp->"
			send "showc\r"
			expect "cmdp->"
			send "showp\r"
			expect "cmdp->"
			send "bye\r"
EOF
		}
		function_cmdataproxy  > $log_path/cmdataproxyvar_"$cmdataproxyvar".log
		set_field_value $path cmdataproxyvar_$cmdataproxyvar ip $cmdataproxyvar
		cat $log_path/cmdataproxyvar_"$cmdataproxyvar".log  | grep "status: except" &>     /dev/null 
		if [ "$?" == 0 ];then
			status=1
			err_info="cmdataproxyvar Connected rabbitmq fail"
        	check_method="telnet "$cmdataproxyvar" ${port};send showc showp"
        	set_field_value $path cmdataproxyvar_$cmdataproxyvar status $status
        	echo "err_info="$err_info"" >> $path
        	echo "check_method="$check_method""    >> $path
		else
			status=0
			set_field_value $path cmdataproxyvar_$cmdataproxyvar status $status
		fi
	else
		status=1
		err_info="no cmdataproxyvar process"
        check_method="telnet "$cmdataproxyvar" ${port}"
        set_field_value $path cmdataproxyvar_$cmdataproxyvar ip $cmdataproxyvar
        set_field_value $path cmdataproxyvar_$cmdataproxyvar status $status
        echo "err_info="$err_info"" >> $path
        echo "check_method="$check_method""    >> $path
	fi
done
