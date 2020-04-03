#!/bin/bash

if [ $# -ne 4 ]; then
    echo "params error"
    exit 1
fi
# 接收4个参数 配置文件路径/打开模式/端口/打开文件路径/
config_path=$1
open_mode=$2   # upload/download
port=$3
open_path=$4

FTP_SERVER=/opt/midware/ftpd/vsftpd
count=1

open_path=${open_path//\//\\/}
sed -i "s/^listen_port.*$/listen_port=${port}/g" "${config_path}"
sed -i "s/^local_root.*$/local_root=${open_path}/g" "${config_path}"
sed -i "s/^anon_root.*$/anon_root=${open_path}/g" "${config_path}"

if [ "${open_mode}" == "upload" ]; then
  sed -i "s/^write_enable.*$/write_enable=YES/g" "${config_path}"
  sed -i "s/^download_enable.*$/download_enable=NO/g" "${config_path}"
  sed -i "s/^anon_upload_enable.*$/anon_upload_enable=YES/g" "${config_path}"
  sed -i "s/^anon_world_readable_only.*$/anon_world_readable_only=NO/g" "${config_path}"
else
  sed -i "s/^write_enable.*$/write_enable=NO/g" "${config_path}"
  sed -i "s/^download_enable.*$/download_enable=YES/g" "${config_path}"
  sed -i "s/^anon_upload_enable.*$/anon_upload_enable=NO/g" "${config_path}"
  sed -i "s/^anon_world_readable_only.*$/anon_world_readable_only=YES/g" "${config_path}"
fi

running=$(netstat -tnlp | grep "${port}" | grep "vsftp")
while [ -z "${running}" ]; do
  if [ ${count} -eq 0 ]; then
    echo "start ftp server failed!!"
    exit 1
  fi

  ${FTP_SERVER} "${config_path}" &>/dev/null
  sleep 1
  running=$(netstat -tnlp | grep "${port}" | grep "vsftp")
  (( count-- ))
done

IFS=" " read -r -a ips <<< "$(hostname -I)"
for ip in "${ips[@]}"; do
  echo "ftp://ftp:luban_upload@${ip}:${port}"
done
exit 0
