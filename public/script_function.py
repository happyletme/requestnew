import datetime,json,re,jsonpath
from public.sqldb import *
from public.log import *
def echo(*args):
    for i in args:
        print ("[time:{asctime}] - INFO : {message}".format(asctime=  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),message=i))

# 断言内置方法
def getAssertWay(assertway):
    if assertway=="assertEqual":
        Assertwaymessage="等于"
    elif assertway=="assertNotEqual":
        Assertwaymessage="不等于"
    elif assertway=="assertRegexpMatches":
        Assertwaymessage="包含"
    elif assertway=="assertNotRegexpMatches":
        Assertwaymessage="不包含"
    elif assertway=="assertGreater":
        Assertwaymessage="大于"
    elif assertway=="assertGreaterEqual":
        Assertwaymessage="大于等于"
    elif assertway=="assertLess":
        Assertwaymessage="小于"
    elif assertway=="assertLessEqual":
        Assertwaymessage="小于等于"
    elif assertway=="assertIn":
        Assertwaymessage="在列表中"
    elif assertway=="assertNotIn":
        Assertwaymessage="不在列表中"
    return Assertwaymessage
#执行sql取出变量
def carry_sql(transferip_db,transferfunction,sqlDatalist,sql_condition,newVariableObj):
    sqlDatalist = replace_newVariableObj(transferfunction,newVariableObj, sqlDatalist)
    makesqldata = None
    for sqlDatalistCount in range(len(sqlDatalist)):
        sqlData = sqlDatalist[sqlDatalistCount]
        if sqlData['sql_condition'] == sql_condition:
            if sqlData['is_select'] != True:
                transferip_db.db[sqlData['db']].ExecNoQuery(sqlData['sql'])
            else:
                makesqldata = MakeSqlData(transferip_db.db[sqlData['db']],sqlData['variable'], sqlData['sql'])
                newVariableObj = dict(newVariableObj, **makesqldata.variableObj)
    return makesqldata,newVariableObj,sqlDatalist
#执行nosql
def carry_nosql(transferip_db,transferfunction,nosqlDatalist,Nosql_condition,newVariableObj):
    nosqlDatalist = replace_newVariableObj(transferfunction,newVariableObj, nosqlDatalist)
    for nosqlDatalistCount in range(len(nosqlDatalist)):
        nosqlData = nosqlDatalist[nosqlDatalistCount]
        if nosqlData['Nosql_condition'] == Nosql_condition:
            #先判断类别
            #把nosql转换成python对象
            Nosql = json.loads(nosqlData['Nosql'])
            #字符串
            if nosqlData['Nosql_dataType']==0:
                if nosqlData['is_select'] != True:
                    if isinstance(Nosql,dict):
                        transferip_db.NoSqlredis.r.mset(Nosql)
                    elif isinstance(Nosql,list):
                        transferip_db.NoSqlredis.delete(Nosql)
                else:
                    variables = nosqlData['variable'].split(',')
                    nosqlvariablesvalue = transferip_db.NoSqlredis.r.mget(Nosql)
                    for nosqlvariablecount in range(len(nosqlvariablesvalue)):
                        if nosqlvariablesvalue[nosqlvariablecount]:
                            nosqlvariablesvalue[nosqlvariablecount] = nosqlvariablesvalue[
                                nosqlvariablecount].decode('utf8')
                    newVariableObj = dict(newVariableObj, **dict(zip(variables,nosqlvariablesvalue)))
            #列表
            elif nosqlData['Nosql_dataType']==1:
                if nosqlData['is_select'] != True:
                    if isinstance(Nosql,dict):
                        transferip_db.NoSqlredis.lpush(Nosql)
                    elif isinstance(Nosql,list):
                        transferip_db.NoSqlredis.delete(Nosql)
                else:
                    variables = nosqlData['variable'].split(',')
                    nosqlvariablesvalue = transferip_db.NoSqlredis.lindex(Nosql)
                    newVariableObj = dict(newVariableObj, **dict(zip(variables, nosqlvariablesvalue)))
    return newVariableObj,nosqlDatalist

#进行变量替换
def replace_newVariableObj(transferfunction,newVariableObj,jsonObj):
    if newVariableObj:
        jsonObj = json.dumps(jsonObj, ensure_ascii=False)
        for i in newVariableObj.keys():
            regex = r"\${" + i + r"}"
            jsonObj = re.sub(regex, str(newVariableObj[i]), jsonObj)
        # 执行自定义函数
        jsonObj=transferfunction.carryfunction.carry_string(jsonObj)
        jsonObj = json.loads(jsonObj)
    else:
        pass
    return jsonObj

# 执行自定义函数
def replace_function(transferfunction,jsonObj):
    jsonObj = json.dumps(jsonObj, ensure_ascii=False)
    jsonObj=transferfunction.carryfunction.carry_string(jsonObj)
    jsonObj = json.loads(jsonObj)
    return jsonObj

#断言
def carry_assert(assert_response,responseJson,status_code,step_name,url,way,headers,params,chooseAssertWay,transferlogname):
    for i in assert_response.keys():
        # 是否不采用数据库断言开关
        switch = 1
        responseJsonAssert = responseJson
        # 走字典方式
        if i[0] == '[':
            # 断言key遍历
            regexkey = r"\[(.+?)\]"
            resultlist = re.findall(regexkey, i)
            regexkey1 = r"'"
            for j in resultlist:
                if len(re.findall(regexkey1, j)) == 0:
                    j = int(j)
                else:
                    j = re.sub(regexkey1, "", j)
                responseJsonAssert = responseJsonAssert[j]
        # 走jsonpath方式(取jsonpath返回数组的第一个值)
        elif i[0] == '.':
            try:
                responseJsonAssert = jsonpath.jsonpath(responseJsonAssert, expr='$' + i)[0]
            except:
                echo(step_name, url, way, headers, params,
                     '请求返回值为: ' + json.dumps(responseJson, ensure_ascii=False))
                errormessage = 'jsonpath按照' + i + '对应路径无法解析返回值  '
                raise RuntimeError(errormessage)
        # 走数据库方式
        elif i[0] == '(':
            switch = 0
            regexkey = r"\((.*?)\)"
            resultlist = re.findall(regexkey, i)
            for k in assert_response[i].keys():
                valuelist = assert_response[i][k].split(',')
            # 断言重写
            try:
                for d in range(len(resultlist)):
                    chooseAssertWay(str(resultlist[d]), k, valuelist[d])
            except:
                @Log(transferlogname.Errorlogname, level="ERROR")
                def writeLog(step_name, url, way, header, params, message, assertResult):
                    print("write Errorlogname")

                Assertwaymessage = getAssertWay(k)
                if str(resultlist[d]):
                    realValue=str(resultlist[d])
                else:
                    realValue = "空字符串"
                writeLog(step_name, url, way, headers, params, "接口测试断言错误",
                    "真实值:" + realValue + ",方式:" + Assertwaymessage + ",预期值:" +
                    valuelist[d])
                echo('请求返回值为: ' + json.dumps(responseJson, ensure_ascii=False))
                chooseAssertWay(str(resultlist[d]), k, valuelist[d])
        # 走返回码校验
        elif i == "status_code":
            responseJsonAssert = status_code
        # 断言
        if switch == 1:
            try:
                for k in assert_response[i].keys():
                    chooseAssertWay(str(responseJsonAssert), k, assert_response[i][k])
            except:
                @Log(transferlogname.Errorlogname, level="ERROR")
                def writeLog(step_name, url, way, header, params, message, assertResult):
                    print("write Errorlogname")

                Assertwaymessage = getAssertWay(k)
                # writeLog(step_name,self.url,way,headers,params,responseJson['message'],str(responseJsonAssert)+Assertwaymessage+assert_response[i][k])
                writeLog(step_name, url, way, headers, params, "用例测试断言错误",
                         i + "真实值:" + str(responseJsonAssert) + ",方式:" + Assertwaymessage + ",预期值:" +
                         assert_response[i][k])
                echo('请求返回值为: ' + json.dumps(responseJson, ensure_ascii=False))
                chooseAssertWay(str(responseJsonAssert), k, assert_response[i][k])
        else:
            pass

    @Log(transferlogname.Successlogname, level="INFO")
    def writeLog(step_name, url, way, header, params, message):
        print("write Successlogname")

    writeLog(step_name, url, way, headers, params, "用例通过")
    echo('请求返回值为: ' + json.dumps(responseJson, ensure_ascii=False))