#-*-coding:utf-8-*-
import pymongo,re
from pymongo import MongoClient
from bson.objectid import ObjectId
from requestnew.settings import MONGODB
class MongoDriver(object):
    def __init__(self, ip='localhost', port=27017):
        self.ip = ip
        self.port = port
        self.init_connect()

    def init_connect(self):
        self.client = MongoClient(self.ip, self.port)

    #选择数据库
    def init_db(self, db,collections):
        self.db = self.client[db]
        self.collections=self.db[collections]

    #插入一条数据
    def insert_one(self,document):
        try:
            self.collections.insert_one(document)
        except Exception as e:
            print (e)

    #查询一条数据
    def search_one(self,test_carryid,api_dependency):
        #搜索结果存于search_result
        search_mongo_result={}
        if api_dependency!={}:
            for variable in api_dependency.keys():
                for reference_step_name in api_dependency[variable].keys():
                    responseJson=self.collections.find_one({"test_carryid":test_carryid,"step_name":reference_step_name})['responseJson']
                    #print (responseJson["object"])

                    responseJsonApi_dependency = responseJson
                    # 断言key遍历
                    regexkey = r"\[(.+?)\]"
                    resultlist = re.findall(regexkey, api_dependency[variable][reference_step_name])
                    regexkey1 = r"'"
                    for j in resultlist:
                        if len(re.findall(regexkey1, j)) == 0:
                            j = int(j)
                        else:
                            j = re.sub(regexkey1, "", j)
                        responseJsonApi_dependency = responseJsonApi_dependency[j]
                search_mongo_result[variable]=responseJsonApi_dependency
        return search_mongo_result

mongodb=MongoDriver(MONGODB['ip'],MONGODB['port'])
mongodb.init_db(MONGODB['NAME'],MONGODB['collections'])

#传递全局变量mongodb数据库对象
class Transferip_mongodb:
    def __init__(self):
        self.mongodb=mongodb
