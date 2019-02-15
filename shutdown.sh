#!/bin/bash

a=`lsof -i:8000|awk 'NR==2{print $2}'`
echo "进程号为"$a
if [[ $a -eq "" ]]
then
   echo "服务已经关闭"
else
   kill -9 $a
   echo "杀死进程后,关闭服务"
fi
