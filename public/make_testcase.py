#-*-coding:utf-8-*-
import os,re
from public.request import *

class Make_testcase:
    def __init__(self,testcasedir,case_data):
        self.testcasedir=testcasedir
        self.case_data=case_data
        self.__getAttributes()
        #self.case_name=case_data['case_name']
        self.filename=self.testcasedir+r"/"+self.case_name+".py"
        self.__create_testcase()
    #生成用例
    def __create_testcase(self):
        try:
            with open(self.filename,'w',encoding='utf-8') as self.testcase:
                message=self.__write()
                self.testcase.write(message)
                self.testcase.close()
        except Exception as e:
            raise e
    #编写用例内容
    def __write(self):
        try:
            templatedir=os.path.abspath(os.path.join(self.testcasedir, "../../template"))
            with open(templatedir, 'r',encoding='utf-8') as self.template:
                templatemessage=self.template.read()
                #regex=r"\${.*?}"
                #替换case_name
                regex = r"\${case_name}"
                message=self.__replaceVariable(regex,self.case_name,templatemessage)
                # 替换case_desc
                regex = r"\${case_desc}"
                message = self.__replaceVariable(regex, self.case_desc, message)
                #替换api
                regex = r"\${api}"
                message = self.__replaceVariable(regex, self.api, message)
                #生成步骤和步骤名
                message=self.__replaceStep(message)
                #print (message)
                self.template.close()
                return message
        except Exception as e:
            raise e

    #替换变量
    def __replaceVariable(self,regex,variable,message,count=0):
        try:
            message = re.sub(regex, variable, message,count)
        except:
            raise ("替换变量出错")
            message=None
        return message

    #根据step_list_data的长度创建几个step
    def __replaceStep(self,message):
        # 根据step_list_data的长度创建几个step
        for i in range(self.steplen):
            stepmessage = '''    def test_${step_name}(self):
        CarryTask.objects.filter(id=self.transferlogname.test_carryid).update(stepcountnow=F('stepcountnow')+1)
        \'\'\'${step_desc}\'\'\'
        step_name="${step_name}"
        newVariableObj = {}
        sqlDatalist=${sqlDatalist}
        nosqlDatalist=${nosqlDatalist}
        api_dependency=${api_dependency}
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
        
        params=\'\'\'${params}\'\'\'
        params=json.loads(params)
        headers=${headers}
        
        # params和headers初始化执行自定义函数
        params=replace_function(self.transferfunction,params)
        headers=replace_function(self.transferfunction,headers)
        
        #replace variable
        params=replace_newVariableObj(self.transferfunction,newVariableObj, params)
        headers=replace_newVariableObj(self.transferfunction,newVariableObj, headers)
        
        responseJson,status_code=${method}(url=self.url,params=params,headers=headers)
        #插入mongodb数据
        document={}
        document['test_carryid'] = self.transferlogname.test_carryid
        document['step_name']=step_name
        document['responseJson'] = responseJson
        self.transfermongodb.mongodb.insert_one(document)
        
        assert_response=${assert_response}
        # assert_response初始化执行自定义函数
        assert_response=replace_function(self.transferfunction,assert_response)
        
        #断言nosql的执行
        newVariableObj,nosqlDatalist=carry_nosql(self.transferip_db,self.transferfunction,nosqlDatalist,1,newVariableObj)
        # 断言sql的执行
        makesqldata, newVariableObj, sqlDatalist = carry_sql(self.transferip_db,self.transferfunction,sqlDatalist, 1,newVariableObj)
        
        #replace assert_response
        assert_response = replace_newVariableObj(self.transferfunction,newVariableObj, assert_response)
            
        way="${way}"
        
        #断言
        carry_assert(assert_response, responseJson, status_code, step_name, self.url, way, headers, params, self.chooseAssertWay,
                     self.transferlogname)
                     
        #后置nosql的执行
        carry_nosql(self.transferip_db,self.transferfunction,nosqlDatalist,2,newVariableObj)
        # 后置sql的执行
        carry_sql(self.transferip_db,self.transferfunction,sqlDatalist, 2,newVariableObj)
'''
            message += stepmessage
        #替换变量
        regexlist = [r"\${step_name}",r"\${step_name}",r"\${step_desc}",r"\${params}",r"\${headers}",r"\${method}",r"\${way}",r"\${assert_response}",r"\${sqlDatalist}",r"\${nosqlDatalist}",r"\${api_dependency}"]
        for i in range(self.steplen):
            j=0
            # 替换步骤名,替换params和headers
            step_name=self.case_data['step_list_data'][i]['step_name']
            message = self.__replaceVariable(regexlist[j], step_name, message,1)
            # 替换步骤名,替换变量
            j += 1
            message = self.__replaceVariable(regexlist[j], step_name, message, 1)

            # 替换step_desc
            j += 1
            step_desc = self.case_data['step_list_data'][i]['step_desc']
            message = self.__replaceVariable(regexlist[j], step_desc, message, 1)

            #替换params
            j += 1
            params = self.case_data['step_list_data'][i]['params']
            message = self.__replaceVariable(regexlist[j], params, message, 1)
            # 替换headers
            j += 1
            headers = self.case_data['step_list_data'][i]['headers']
            message = self.__replaceVariable(regexlist[j], headers, message, 1)
            # 替换method
            j += 1
            method = self.case_data['step_list_data'][i]['method']
            message = self.__replaceVariable(regexlist[j], method, message, 1)
            # 替换way
            j += 1
            way = method
            message = self.__replaceVariable(regexlist[j], way, message, 1)
            # 替换断言
            j += 1
            if self.case_data['step_list_data'][i]['assert_response']=="":
                message = self.__replaceVariable(regexlist[j], "{}", message, 1)
            else:
                message = self.__replaceVariable(regexlist[j], self.case_data['step_list_data'][i]['assert_response'], message, 1)
            # 替换sql
            j += 1
            if len(self.case_data['step_list_data'][i]['sql_list_data']) == 0:
                message = self.__replaceVariable(regexlist[j], "[]", message, 1)
            else:
                sqlDatalist=[]
                for sqlData in self.case_data['step_list_data'][i]['sql_list_data']:
                    sqlDatalist.append(sqlData)
                message = self.__replaceVariable(regexlist[j],str(sqlDatalist), message, 1)
            # 替换nosql
            j += 1
            if len(self.case_data['step_list_data'][i]['nosql_list_data']) == 0:
                message = self.__replaceVariable(regexlist[j], "[]", message, 1)
            else:
                nosqlDatalist = []
                for nosqlData in self.case_data['step_list_data'][i]['nosql_list_data']:
                    nosqlDatalist.append(nosqlData)
                message = self.__replaceVariable(regexlist[j], str(nosqlDatalist), message, 1)
            # 替换接口依赖
            j += 1
            if self.case_data['step_list_data'][i]['api_dependency'] == "":
                message = self.__replaceVariable(regexlist[j], "{}", message, 1)
            else:
                message = self.__replaceVariable(regexlist[j],
                                                    self.case_data['step_list_data'][i]['api_dependency'], message, 1)
        #print (message)
        return message
    #得到属性
    def __getAttributes(self):
        self.case_name = self.case_data['case_name']
        self.api = self.case_data['api']
        self.case_desc = self.case_data['case_desc']
        self.steplen=len(self.case_data['step_list_data'])
        #得到每个脚本的sql数
        self.stepSqllen=[]
        for i in range(self.steplen):
            self.stepSqllen.append(len(self.case_data['step_list_data'][i]['sql_list_data']))
        #self.step_name=self.case_data['step_list_data']['step_name']
