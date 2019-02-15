#!/usr/bin/python
#-*- encoding:UTF-8 -*-

from public.request import *
from public.sqldb import *
from public.log import *
from public.run import *
from public.sqldb import Transferip_db
from public.mongodb import Transferip_mongodb
from public.carryfunction import Transferfunction
from public.script_function import *
from django.db.models import F
import unittest,re,json,jsonpath
class UserLogin(unittest.TestCase):
    '''测试'''
    @classmethod
    def setUpClass(cls):
        cls.transferlogname=Transferlogname()
        cls.transferip_db=Transferip_db()
        cls.transfermongodb = Transferip_mongodb()
        cls.transferfunction = Transferfunction()
        api="/cloud-permission/user/login.do"
        cls.url=cls.transferip_db.ip+api
        pass

    @classmethod
    def tearDownClass(cls):
        pass



    def test_UserLoginMobileError(self):
        CarryTask.objects.filter(id=self.transferlogname.test_carryid).update(stepcountnow=F('stepcountnow')+1)
        '''测试'''
        step_name="UserLoginMobileError"
        newVariableObj = {}
        sqlDatalist=[{'sql_condition': 0, 'is_select': False, 'variable': '', 'sql': 'update request_project set project_name=2 where project_name=1;', 'db': '1', 'db_remark': '云账号'}, {'sql_condition': 1, 'is_select': True, 'variable': 'status', 'sql': 'select status from request_project where id=1;', 'db': '2', 'db_remark': '阿里云服务器'}]
        nosqlDatalist=[]
        api_dependency={}
        #查找接口依赖数据
        search_mongo_result=self.transfermongodb.mongodb.search_one(self.transferlogname.test_carryid,api_dependency)
        #追加替换变量字典
        newVariableObj.update(search_mongo_result)
        
        #sql和nosql初始化执行自定义函数
        nosqlDatalist=replace_function(self.transferfunction,nosqlDatalist)
        sqlDatalist=replace_function(self.transferfunction,sqlDatalist)
        
        #前置nosql的执行
        newVariableObj,nosqlDatalist=carry_nosql(self.transferip_db,self.transferfunction,nosqlDatalist,0,newVariableObj)
        #前置sql的执行
        makesqldata, newVariableObj, sqlDatalist=carry_sql(self.transferip_db,self.transferfunction,sqlDatalist,0,newVariableObj)
        
        params='''{"phone":"14100001111","password":"e10adc3949ba59abbe56e057f20f883e"}'''
        params=json.loads(params)
        headers={"version":"4"}
        
        # params和headers初始化执行自定义函数
        params=replace_function(self.transferfunction,params)
        headers=replace_function(self.transferfunction,headers)
        
        #replace variable
        params=replace_newVariableObj(self.transferfunction,newVariableObj, params)
        headers=replace_newVariableObj(self.transferfunction,newVariableObj, headers)
        
        responseJson,status_code=get(url=self.url,params=params,headers=headers)
        #插入mongodb数据
        document={}
        document['test_carryid'] = self.transferlogname.test_carryid
        document['step_name']=step_name
        document['responseJson'] = responseJson
        self.transfermongodb.mongodb.insert_one(document)
        
        assert_response={".msg":{"assertEqual":"手机号格式不正确"},".code":{"assertEqual":"1"}}
        # assert_response初始化执行自定义函数
        assert_response=replace_function(self.transferfunction,assert_response)
        
        #断言nosql的执行
        newVariableObj,nosqlDatalist=carry_nosql(self.transferip_db,self.transferfunction,nosqlDatalist,1,newVariableObj)
        # 断言sql的执行
        makesqldata, newVariableObj, sqlDatalist = carry_sql(self.transferip_db,self.transferfunction,sqlDatalist, 1,newVariableObj)
        
        #replace assert_response
        assert_response = replace_newVariableObj(self.transferfunction,newVariableObj, assert_response)
            
        way="get"
        
        #断言
        carry_assert(assert_response, responseJson, status_code, step_name, self.url, way, headers, params, self.chooseAssertWay,
                     self.transferlogname)
                     
        #后置nosql的执行
        carry_nosql(self.transferip_db,self.transferfunction,nosqlDatalist,2,newVariableObj)
        # 后置sql的执行
        carry_sql(self.transferip_db,self.transferfunction,sqlDatalist, 2,newVariableObj)
    def test_UserLoginMobileError1(self):
        CarryTask.objects.filter(id=self.transferlogname.test_carryid).update(stepcountnow=F('stepcountnow')+1)
        '''测试'''
        step_name="UserLoginMobileError1"
        newVariableObj = {}
        sqlDatalist=[{'sql_condition': 0, 'is_select': False, 'variable': '', 'sql': 'update request_project set project_name=2 where project_name=1;', 'db': '1', 'db_remark': '云账号'}, {'sql_condition': 1, 'is_select': True, 'variable': 'id,status', 'sql': 'select id,status from request_project where id=1;', 'db': '2', 'db_remark': '阿里云服务器'}]
        nosqlDatalist=[]
        api_dependency={}
        #查找接口依赖数据
        search_mongo_result=self.transfermongodb.mongodb.search_one(self.transferlogname.test_carryid,api_dependency)
        #追加替换变量字典
        newVariableObj.update(search_mongo_result)
        
        #sql和nosql初始化执行自定义函数
        nosqlDatalist=replace_function(self.transferfunction,nosqlDatalist)
        sqlDatalist=replace_function(self.transferfunction,sqlDatalist)
        
        #前置nosql的执行
        newVariableObj,nosqlDatalist=carry_nosql(self.transferip_db,self.transferfunction,nosqlDatalist,0,newVariableObj)
        #前置sql的执行
        makesqldata, newVariableObj, sqlDatalist=carry_sql(self.transferip_db,self.transferfunction,sqlDatalist,0,newVariableObj)
        
        params='''{"phone":"14100001111","password":"e10adc3949ba59abbe56e057f20f883e"}'''
        params=json.loads(params)
        headers={"version":"4"}
        
        # params和headers初始化执行自定义函数
        params=replace_function(self.transferfunction,params)
        headers=replace_function(self.transferfunction,headers)
        
        #replace variable
        params=replace_newVariableObj(self.transferfunction,newVariableObj, params)
        headers=replace_newVariableObj(self.transferfunction,newVariableObj, headers)
        
        responseJson,status_code=get(url=self.url,params=params,headers=headers)
        #插入mongodb数据
        document={}
        document['test_carryid'] = self.transferlogname.test_carryid
        document['step_name']=step_name
        document['responseJson'] = responseJson
        self.transfermongodb.mongodb.insert_one(document)
        
        assert_response={".msg":{"assertEqual":"手机号格式不正确"},".code":{"assertEqual":"1"}}
        # assert_response初始化执行自定义函数
        assert_response=replace_function(self.transferfunction,assert_response)
        
        #断言nosql的执行
        newVariableObj,nosqlDatalist=carry_nosql(self.transferip_db,self.transferfunction,nosqlDatalist,1,newVariableObj)
        # 断言sql的执行
        makesqldata, newVariableObj, sqlDatalist = carry_sql(self.transferip_db,self.transferfunction,sqlDatalist, 1,newVariableObj)
        
        #replace assert_response
        assert_response = replace_newVariableObj(self.transferfunction,newVariableObj, assert_response)
            
        way="get"
        
        #断言
        carry_assert(assert_response, responseJson, status_code, step_name, self.url, way, headers, params, self.chooseAssertWay,
                     self.transferlogname)
                     
        #后置nosql的执行
        carry_nosql(self.transferip_db,self.transferfunction,nosqlDatalist,2,newVariableObj)
        # 后置sql的执行
        carry_sql(self.transferip_db,self.transferfunction,sqlDatalist, 2,newVariableObj)
