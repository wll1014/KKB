# Django2.2
## 需要修改源码内容
1. django/db/backends/mysql/base.py  注释 35-36行
1. django/db/backends/mysql/operations.py  注释145-146行

如使用pymysql，需要修改以上两点，否则无法执行数据库迁移

所以使用mysqlclient

---

## ElasticSearch集群
集群时，配置文件（conf/ops.ini），[elasticsearch]的hosts可填写多个地址，以逗号(,)分隔，逗号前后不可有空格

---

## 初始化json导入导出方式
以sidebar举例，导出方法
- 导出
`python3 manage.py dumpdata sidebar.ModelSidebar > sidebar.json`
- 导入
`python3 manage.py loaddata sidebar.json`


## install.sh脚本使用
1. 正常执行，即正常安装
`./install.sh`
2. 传入flag参数 1，不执行安装操作，执行清空数据库，并执行migrate
`./install.sh 1`

## 增加依赖包的下载即安装
1. 下载离线安装包至requirement_package
`pip3 download ipip-ipdb -d ./requirement_package -i https://pypi.douban.com/simple/`
2. 在requirement.txt中添加要增加的包名及版本
3. 安装时脚本会自动按照requirement.txt在requirement_package寻找本地安装包安装到指定路径
