#!/bin/sh

#main version & extension version
version=6.0.0.0
myDate="$version.$(date '+%Y%m%d%H%M')"


function package() {
    key=${1}
    path="../../../31-ops/watcher"
    mkdir -p ${path}/files_temp/${key}/
    mkdir -p ${path}/release/${key}/
    rm ${path}/release/${key}/* -rf
    # 版本号
    echo ${myDate} > ${path}/files_temp/${key}/version
    
    cp -ar ${path}/${key} ${path}/files_temp/
    cp -ar ${path}/common/ ${path}/files_temp/${key}/
    cp -ar ${path}/common_lib/ ${path}/files_temp/${key}/

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

package mqwatcher

rm ${path}/files_temp/${key}/ -rf 
