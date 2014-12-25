#!/bin/sh
echo 'TODO'
exit

cd `dirname $0`/../src

rm -rf ../project
rm -f ./project.tar.gz
mkdir ../project
cp -r ./* ../project/

cd ../
tar -czvf ./project.tar.gz ./project

scp ./project.tar.gz hal9000@192.168.1.30:/home/hal9000/project.tar.gz

rm -rf ../project
rm -f ./project.tar.gz

ssh hal9000@192.168.1.30 "cd /home/hal9000/;rm -rf ./project;tar zxf ./project.tar.gz;rm ./project.tar.gz;rm -rf /home/hal9000/.xbmc/addons/script.module.xbmcup/*;cp -r ./project/* /home/hal9000/.xbmc/addons/script.module.xbmcup/"
