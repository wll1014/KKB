#!/usr/bin/env bash

version=6.0.0.3.0
myDate="${version}-`date '+%Y%m%d%H%M'`"

function package() {
    path=$(cd ../../../31-ops;pwd)
    key=${1}
    mkdir -p ${path}/files_temp/${key}/
    mkdir -p ${path}/release/${key}/
    rm ${path}/release/${key}/* -rf
    # 版本号
    echo ${myDate} > ${path}/files_temp/${key}/version

    # 后端打包
    cp -ar ${path}/${key} ${path}/files_temp/

    # 前端打包
    cd ${path}/ops_vue/
	echo "begin package..."
    ./package.sh ${path}/ops_vue
	echo "end package..."
	cd -
	  cp -ar ${path}/ops_vue/dist/* ${path}/files_temp/${key}/static/
	  
    if [ -d ${path}/files_temp/${key}/release ];then
        rm ${path}/files_temp/${key}/release -rf
    fi
    if [ -d ${path}/files_temp/${key}/files_temp ];then
        rm ${path}/files_temp/${key}/files_temp -rf
    fi
    if [ -f ${path}/files_temp/${key}/compile.sh ];then
	    rm ${path}/files_temp/${key}/compile.sh -f
	fi
    cd ${path}/files_temp/

    tar -zcf ${path}/release/${key}/${key}.tar.gz ${key}/
    cd -
}

package ops_server

rm ${path}/files_temp/${key}/ -rf
