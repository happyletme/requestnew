#!/usr/bin/python
#-*- encoding:UTF-8 -*-
import os,unittest,time,sys
from public.log import *
#from public.HTMLTestRunner import *
#import HTMLTestRunner,os,time
import os,time,uuid
from public.suit import *
from public.system import rm_file
from public.spider import  Spider
from request.models import *
from django.db.models import Min,Avg,Max,Sum
from public.email import SendEmail
from public.ExtentHTMLTestRunner import HTMLTestRunner
from publicExpansion.emailBody import makeEamilBody

#将文件的全局变量通过类属性传递给脚本文件
class Transferlogname:
    def __init__(self):
        self.successlogname=successlogname
        self.errorlogname=errorlogname
        self.test_carryid=test_carryid

def interface(task_name,failcount,email_data,env_desc,nosqldb_desc,out_id,test_carryTaskid):
    #获取权重
    case_names_weights={}
    task_cases=Task.objects.filter(task_name=task_name).values("case_id","uuid")
    for task_case in task_cases:
        UUID=task_case['uuid']
        case_steps=Case.objects.filter(id=task_case['case_id']).values("case_name","case_weights")
        for case_step in case_steps:
            case_names_weights[case_step['case_name']]=case_step['case_weights']

    task_dir=os.getcwd()+r"/task/"+task_name+"---"+UUID
    timer = time.strftime("%y-%m-%d%H-%M-%S", time.localtime(time.time()))
    #print (os.getcwd())
    #report_dir=os.getcwd()+"/report/"
    report_dir=task_dir+r"/report"
    #文件名字
    filename=report_dir+r"/report"+timer+".html"
    #print filename
    fp=open(filename,"wb")

    #日志服务
    global successlogname
    Successlogname = report_dir+r"/Successlog"+timer+".text"
    try:
        successlogname.update({str(test_carryTaskid) + "successlogname": report_dir+r"/Successlog"+timer+".text"})
    except:
        successlogname = {str(test_carryTaskid) + "successlogname": report_dir+r"/Successlog"+timer+".text"}

    global errorlogname
    Errorlogname = report_dir + r"/Successlog" + timer + ".text"
    try:
        errorlogname.update({str(test_carryTaskid) + "errorlogname": report_dir + r"/Errorlog"+timer+ ".text"})
    except:
        errorlogname = {str(test_carryTaskid) + "errorlogname": report_dir + r"/Errorlog"+timer+ ".text"}


    #目录名字
    #case_dir=os.getcwd()+"/testcase/"
    case_dir=task_dir+r"/testcase"


    def createSuite():
        #suiteunit=unittest.TestSuite()
        #对应suit进行重构，调用重构的
        #global stepcountall
        stepcountall=0
        suiteunit=Suit()
        suiteunit.editfailcount(failcount)
        os.path.abspath(os.path.join(task_dir, "../"))
        discover=unittest.defaultTestLoader.discover(case_dir,case_names_weights,pattern="*.py",top_level_dir=os.path.abspath(os.path.join(task_dir, "../")))

        for test_suite in discover:
            #print (test_suite)
            for i in test_suite:
                #统计步骤总数
                for _ in i:
                     stepcountall+=1
                suiteunit.addTests(i)
        return(suiteunit,stepcountall)

    #suiteunit=unittest.TestSuite()
    #discover=unittest.defaultTestLoader.discover(case_dir,pattern="*.py",top_level_dir=None)
    #原始报告
    #runner = HTMLTestRunner.HTMLTestRunner(stream=fp,title=u'测试',description=u'接口报告的描述')
    #新报告
    runner = HTMLTestRunner(stream=fp, title=task_name.split('---')[0], description=u'接口报告的描述')
    testsuite,stepcountall=createSuite()
    CarryTask.objects.filter(task_name=task_name, out_id=out_id).update( htmlreport=filename, successlogname=Successlogname,
                             errorlogname=Errorlogname, stepcountall=stepcountall)

    # 将这次是第几次执行写入mongo数据库
    global test_carryid
    try:
        test_carryid = test_carryTaskid
    except:
        # 第一次执行时
        test_carryid = 1

    runner.run(testsuite)
    fp.close()

    # 任务表的carrystatus置成3
    Task.objects.filter(task_name=task_name).update(carrystatus=3)

    #开始拿去报告和日志的数据
    spider = Spider(filename)
    test_steps, statuses = spider.get_html_data()
    spider.get_log_data(Successlogname, Errorlogname)
    responses = spider.get_response(test_steps,statuses)

    #获取用例名和用例对应的api
    test_stepCuts=[]
    apis=[]
    statusesMessages=[]
    result = []
    title = ['用例名','接口路径','状态']
    # 状态中文
    for statuse in statuses:
        if statuse == 0:
            statusesMessage = "非断言性错误"
        elif statuse == 1:
            statusesMessage = "成功"
        elif statuse == 2:
            statusesMessage = "断言性错误"
        statusesMessages.append(statusesMessage)

    #把执行数据全部入库
    #如果正常
    try:
        for i in range(len(test_steps)):
            LogAndHtmlfeedback.objects.create(test_step=test_steps[i],test_status=statuses[i],test_response=responses[i],test_carryTaskid=test_carryTaskid)

            #邮件数据准备
            #用例名
            test_stepCut = test_steps[i][5:]
            test_stepCuts.append(test_stepCut)
            # api
            caseId = Step.objects.filter(step_name=test_stepCut).values('case')[0]['case']
            api = Case.objects.filter(id=caseId).values('api')[0]['api']
            apis.append(api)
        # 得到邮件正文html
        result.append(test_stepCuts)
        result.append(apis)
        result.append(statusesMessages)
        body=makeEamilBody(result,title,task_name,env_desc,nosqldb_desc)
    # 如果全部是内部错误返回，不生成文件
    except:
        for i in range(len(test_steps)):
            LogAndHtmlfeedback.objects.create(test_step=test_steps[i],test_status=statuses[i],test_response="",test_carryTaskid=test_carryTaskid)

            # 邮件数据准备
            # 用例名
            test_stepCut = test_steps[i][5:]
            test_stepCuts.append(test_stepCut)
            # api
            caseId = Step.objects.filter(step_name=test_stepCut).values('case')[0]['case']
            api = Case.objects.filter(id=caseId).values('api')[0]['api']
            apis.append(api)
        # 得到邮件正文html
        result.append(test_stepCuts)
        result.append(apis)
        result.append(statusesMessages)
        body = makeEamilBody(result, title, task_name, env_desc, nosqldb_desc)

    # 判断是否发送邮件是则发送
    if email_data != None:
        logs = {"successlog": Successlogname, "errorlog": Errorlogname, "report": filename}
        sendemail = SendEmail(email_data['host_dir'], email_data['email_port'], email_data['username'],
                              email_data['passwd'])
        sendemail.add_message(body, logs)
        sendemail.add_header(email_data['Headerfrom'], email_data['Headerto'], email_data['subject'])
        sendemail.send(email_data['sender'], email_data['receivers'].split(','))
    return filename


'''
if __name__=="__main__":
    interface("task")
'''