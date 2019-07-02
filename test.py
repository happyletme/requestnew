#!/usr/bin/python
# -*- encoding:UTF-8 -*-

from public.request import *
from public.sqldb import *
from public.log import *
from public.run import *
from public.sqldb import Transferip_db
from public.mongodb import Transferip_mongodb
from public.carryfunction import Transferfunction
from public.script_function import *
from django.db.models import F
import unittest, re, json, jsonpath


class VB(unittest.TestCase):
    '''添加'''

    @classmethod
    def setUpClass(cls):
        cls.transferlogname = Transferlogname()
        cls.transferip_db = Transferip_db()
        cls.transfermongodb = Transferip_mongodb()
        cls.transferfunction = Transferfunction()
        api = "http://192.168.30.164:8082/bnms/web-bn/patientList "
        cls.url = cls.transferip_db.ip + api
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_添加患者信息(self):
        CarryTask.objects.filter(id=self.transferlogname.test_carryid).update(stepcountnow=F('stepcountnow') + 1)
        ''''''
        step_name = "添加患者信息"
        newVariableObj = {}
        sqlDatalist = []
        nosqlDatalist = []
        api_dependency = {}
        # 查找接口依赖数据
        search_mongo_result = self.transfermongodb.mongodb.search_one(self.transferlogname.test_carryid, api_dependency)
        # 追加替换变量字典
        newVariableObj.update(search_mongo_result)

        # sql和nosql初始化执行自定义函数
        nosqlDatalist = replace_function(self.transferfunction, nosqlDatalist)
        sqlDatalist = replace_function(self.transferfunction, sqlDatalist)

        # 前置nosql的执行
        newVariableObj, nosqlDatalist = carry_nosql(self.transferip_db, self.transferfunction, nosqlDatalist, 0,
                                                    newVariableObj)
        # 前置sql的执行
        makesqldata, newVariableObj, sqlDatalist = carry_sql(self.transferip_db, self.transferfunction, sqlDatalist, 0,
                                                             newVariableObj)

        params = '''{"patientIn":{"patientId":null,"patientCardId":"11","deptId":"1001","personIdNo":null,"inFqcy":1,"patientName":"张晓明","sex":"男","doctorName":null,"nurseName":null,"inpNo":"A10101","bedName":"01","nurseLevel":null,"orgId":null,"createUser":null,"birthday":"2018-01-01 12:22:22","createTime":null,"inTime":"2018-01-01 22:22:22"}}'''
        params = json.loads(params)
        headers = {}

        # params和headers初始化执行自定义函数
        params = replace_function(self.transferfunction, params)
        headers = replace_function(self.transferfunction, headers)

        # replace variable
        params = replace_newVariableObj(self.transferfunction, newVariableObj, params)
        headers = replace_newVariableObj(self.transferfunction, newVariableObj, headers)

        responseJson, status_code = postbody(url=self.url, params=params, headers=headers)
        # 插入mongodb数据
        document = {}
        document['test_carryid'] = self.transferlogname.test_carryid
        document['step_name'] = step_name
        document['responseJson'] = responseJson
        self.transfermongodb.mongodb.insert_one(document)

        assert_response = {"status": {"assertEqual": "200"}}
        # assert_response初始化执行自定义函数
        assert_response = replace_function(self.transferfunction, assert_response)

        # 断言nosql的执行
        newVariableObj, nosqlDatalist = carry_nosql(self.transferip_db, self.transferfunction, nosqlDatalist, 1,
                                                    newVariableObj)
        # 断言sql的执行
        makesqldata, newVariableObj, sqlDatalist = carry_sql(self.transferip_db, self.transferfunction, sqlDatalist, 1,
                                                             newVariableObj)

        # replace assert_response
        assert_response = replace_newVariableObj(self.transferfunction, newVariableObj, assert_response)

        way = "postbody"

        # 断言
        carry_assert(assert_response, responseJson, status_code, step_name, self.url, way, headers, params,
                     self.chooseAssertWay,
                     self.transferlogname)

        # 后置nosql的执行
        carry_nosql(self.transferip_db, self.transferfunction, nosqlDatalist, 2, newVariableObj)
        # 后置sql的执行
        carry_sql(self.transferip_db, self.transferfunction, sqlDatalist, 2, newVariableObj)
