#!/usr/bin/env python
# -*- coding:utf8 -*-

import redis

class Redis:
    def __init__(self,host,port=6379,password=None):
        self.connect(host,port,password)
    #设置连接池
    def connect(self,host,port,password):
        pool = redis.ConnectionPool(host=host,port=port,password=password)  # 实现一个连接池
        self.r = redis.Redis(connection_pool=pool)
    #list从右向左插入数据
    def lpush(self,listdata):
        # 插入之前先删数据
        self.r.delete(*listdata.keys())
        for i in listdata.keys():
            self.r.lpush(i,*listdata[i])
    #list读取单个数据
    def lindex(self,indexdata):
        listvalue=[]
        for i in indexdata.keys():
            try:
                listvalue.append(self.r.lindex(i,indexdata[i]).decode('utf8'))
            except:
                listvalue.append(None)
        return listvalue
    def delete(self,keysdata):
        self.r.delete(*keysdata)

'''
host='10.1.6.125'
redis=Redis(host)
#redis.get("foo")
redis.lpush({'foo':[1,2,3],'foo1':['a','b','c']})
#listvalue=redis.lindex({'foo':1,'foo1':0})
#redis.delete(['foo','foo1'])
'''