#!/usr/bin/env python
# -*- coding:utf8 -*-

import time,datetime
class Expandfunction:
    def __init__(self):
        pass
    #获取当前时间
    def getNowTime(self,format):
        return time.strftime(format, time.localtime(time.time()))
    #设置固定时间等待
    def wait_time(self,seconds):
        time.sleep(seconds)
        return ""
    #获取几天后的那天开始的时间戳
    def get_start_Timestamp(self,day):
        today = datetime.date.today()
        thatday = today + datetime.timedelta(days=day)
        thatday_start_time = str(int(time.mktime(time.strptime(str(thatday), '%Y-%m-%d')))) + "000"
        return thatday_start_time







