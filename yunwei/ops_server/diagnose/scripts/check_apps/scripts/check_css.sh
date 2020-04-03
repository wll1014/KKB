#!/bin/bash
kdf=/opt/data/luban/shells
. $kdf/kdfunctions
ssh_port=22223
ip_info=$1
log_path=$2
path=$3
css=`cat $ip_info |grep css |cut -d '=' -f 2`
css=($css)
num=${#css[@]} 
if [ $num == 0 ]; then
    echo  -e "\e[1;31m Error:获取css的IP失败！\e[0m" 
    exit 
fi

for cssvar in ${css[@]};
do
    port=$(ssh -o StrictHostKeyChecking=no -p 33332 root@$cssvar netstat -tnlp | grep css | awk '{print $4}' | awk -F":" '{print $2}')
    echo -e "\n"|telnet $cssvar ${port} 2>/dev/null | grep -q Connected
    if [ "$?" == "0" ];then 
        function_css(){
                /usr/bin/expect << EOF
			    spawn telnet $cssvar ${port}
				expect "Username:"
				send "\r"
				expect "Password:"
				send "\r"
				expect "css->"
				send "check\r"
                expect "css->"
                send "showcmu\r"
                expect "css->"
                send "bmaster\r"                
				expect "css->"
				send "bye\r"
EOF
}
        function_css  > $log_path/css_"$cssvar".log
        ###主从状态######
        cat $log_path/css_"$cssvar".log |grep "当前为:从" &>     /dev/null 
        if [ "$?" == 0 ];then
            master_slave=slave
        else
            master_slave=master
        fi
        set_field_value $path css_$cssvar ip $cssvar
        set_field_value $path css_$cssvar master_slave $master_slave
        cat $log_path/css_"$cssvar".log |grep -P '\Q[fail]\E' &>     /dev/null 
        if [ "$?" == 0 ];then
            status=1
            err_info="css $cssvar check fail"
            check_method="telnet $cssvar ${port};send check"
            set_field_value $path css_$cssvar status $status
            echo "err_info="$err_info"" >> $path
            echo "check_method="$check_method""    >> $path
        else
            status=0
            flag=0
            set_field_value $path css_$cssvar status $status
        fi
        mcu_num=`cat $log_path/css_"$cssvar".log |grep "is Enable"|grep "McuIp" |wc -l` 
        if [ "$mcu_num" == 0 ];then
            status=1
            if [ "$flag" == 0 ];then
                err_info="css has no cmu"
                check_method="telnet "$cssvar" ${port};send showcmu"
                set_field_value $path css_$cssvar status $status
                echo "err_info="$err_info"" >> $path
                echo "check_method="$check_method""    >> $path
            else
                err_info_1="css has no cmu"
                check_method_1="telnet "$cssvar" ${port};send showcmu"
                set_field_value $path css_$cssvar status $status
                echo "err_info_1="$err_info_1"" >> $path
                echo "check_method_1="$check_method_1""    >> $path
            fi
        fi
    else
        status=1
        err_info="no css process"
        check_method="telnet "$cssvar" ${port}"
        set_field_value $path css_$cssvar ip $cssvar
        set_field_value $path css_$cssvar status $status
        echo "err_info="$err_info"" >> $path
        echo "check_method="$check_method""    >> $path
    fi




done
