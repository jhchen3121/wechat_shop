#!/bin/sh
#-*- coding:utf-8 -*- 

# ！！说明：入口参数为mysql root用户密码, 新建数据库密码与root密码一致

if [ -z "$PROJ_NAME" ];then
    echo PROJ_DIR not set
    exit 1
fi

if [ ! -n "$1" ];then
    echo 'please input password, ex: sh init-mysql-database.sh yourpasswd'
    exit 1
fi

proj_name=$PROJ_NAME
proj_db="${proj_name}db"
password=$1

echo "Project Name: $proj_name"
echo "MySQL username: $proj_name"
echo "MySQL password: $1"
echo "MySQL Database: $proj_db"

#cat << EOF|mysql -uroot -v -pMyNewPass4!| sed -e '/^$/d' -e '/----/d' -e 's/^/\t[-] /'
#drop database if exists ${proj_db};
#create database ${proj_db} default character set = utf8;
#EOF
#
#cat << EOF|mysql -uroot -v -pMyNewPass4!| sed -e '/^$/d' -e '/----/d' -e 's/^/\t[-] /'
#drop user '${proj_name}'@'localhost';
#EOF
#
#cat << EOF|mysql -uroot -v -pMyNewPass4!| sed -e '/^$/d' -e '/----/d' -e 's/^/\t[-] /'
#create user '${proj_name}'@'localhost' identified by 'MyNewPass4!';
#grant all on ${proj_db}.* to '${proj_name}'@'localhost';
#EOF

cat << EOF|mysql -uroot -v -p${password}| sed -e '/^$/d' -e '/----/d' -e 's/^/\t[-] /'
drop database if exists ${proj_db};
create database ${proj_db} default character set = utf8;
EOF

cat << EOF|mysql -uroot -v -p${password}| sed -e '/^$/d' -e '/----/d' -e 's/^/\t[-] /'
drop user '${proj_name}'@'localhost';
EOF

cat << EOF|mysql -uroot -v -p${password}| sed -e '/^$/d' -e '/----/d' -e 's/^/\t[-] /'
create user '${proj_name}'@'localhost' identified by '${password}';
grant all on ${proj_db}.* to '${proj_name}'@'localhost';
EOF
