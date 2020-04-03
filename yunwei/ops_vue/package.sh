#!/bin/bash -x
PS4='$(date "+%s.%N ($LINENO) + ")'
ops_path=$1
cd $ops_path
WORK=$(pwd)

if [ -d node_modules ];then
    rm -rf node_modules
    rm -rf node-v10.16.0-linux-x64
fi
tar -xf node-v10.16.0-linux-x64.tar.xz  
tar -zxf node_modules.tar.gz

export PATH=$PATH:$WORK/node-v10.16.0-linux-x64/bin
#npm install
npm run build

rm -rf node_modules
rm -rf node-v10.16.0-linux-x64

cd -