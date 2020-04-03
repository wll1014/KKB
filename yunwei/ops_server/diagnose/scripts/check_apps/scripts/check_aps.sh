#!/bin/bash
kdf=/opt/data/luban/shells
. $kdf/kdfunctions
ip_info=$1
path=$3
aps=`cat $ip_info |grep aps |cut -d '=' -f 2`
aps=($aps)
num=${#aps[@]} 
if [ $num == 0 ]; then
    echo  -e "\e[1;31m Error:获取aps的IP失败！\e[0m" 
    exit 
fi

for apsvar in ${aps[@]};
do
    aps_status=`curl -s http://"$apsvar":60081/aps/check`
    if [ "$aps_status" == "running" ];then
    	status=0
    	set_field_value $path aps_$apsvar ip $apsvar
		set_field_value $path aps_$apsvar status $status
    else
        status=1
        err_info=$aps_status
        check_method="curl -s http://"$apsvar":60081/aps/check"
        set_field_value $path aps_$apsvar ip $apsvar
		set_field_value $path aps_$apsvar status $status
        echo "err_info="$err_info"" >> $path
        echo "check_method="$check_method""    >> $path

    fi
done
