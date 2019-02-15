#!/bin/bash
nohup python3 /home/pj/requestnew/manage.py runserver 0.0.0.0:8000 >> ../logs/request.log &
echo "启动成功"
