#-*-coding:utf-8-*-
from bs4 import BeautifulSoup
import re
class Spider:
    def __init__(self,htmlname):
        try:
            with open(htmlname,'rb') as self.fp:
                self.bsobj = BeautifulSoup(self.fp.read())
        except FileNotFoundError as e:
            self.bsobj=None
            print (e)
    #获取html数据
    def get_html_data(self):
        test_cases = []
        statuses = []
        if self.bsobj:
            test_stephtmls = self.bsobj.find_all('div', {"class": "node-name"})
            for i in test_stephtmls:
                test_cases.append(i.get_text())
                #记录pass,error,fail
                teststepresult=i.parent.find_all("span")[1].get_text()
                #pass
                if teststepresult=="pass":
                    statuses.append(1)
                #系统错误的用例
                elif teststepresult=="error":
                    statuses.append(0)
                #断言错误的用例
                elif teststepresult == "fail":
                    statuses.append(2)

            self.fp.close()
        return test_cases,statuses
    #日志记录存入列表
    def get_log_data(self,*lognames):
        self.lognamelist=[]
        for logname in lognames:
            try:
                for line in open(logname):
                    newline=re.findall("INFO : (.*)",line)
                    if len(newline)==0:
                        newline = re.findall("ERROR : (.*)", line)
                    #print (newline[0])
                    self.lognamelist.append(newline[0])
            except FileNotFoundError as e:
                print (e)
        return self.lognamelist
    #根据步骤名获取反馈
    def get_response(self,test_steps,statuses):
        #print (test_cases)
        responses=[]
        #i=1说明找到步骤名取下面第5个
        i=0
        a=0
        for test_case in test_steps:
            #根据日志是正确的还是错误的判断行循环次数取值
            if statuses[a] == 1:
                cycle = 5
            else:
                cycle = 6
            a+=1
            # j控制5次循环
            j = 0
            #可能存在重复step得把已取的lognamelist中的内容置换成已读
            k=0
            for logmessage in self.lognamelist:
                k+=1

                #如果循环cycle次之后需要把i重置
                if j==cycle:
                    i=0
                    j=0
                    responses.append(logmessage)
                    #print(logmessage)
                    break
                # 如果k为lognamelist的列表长，就在responses里添加一个空字符串
                if k == len(self.lognamelist):
                    responses.append("")
                #print(logmessage)
                if test_case[5:]==logmessage:
                    #print (logmessage)
                    self.lognamelist[k-1]="alreadyget"
                    i=1
                if i==1:
                    j+=1
                    continue
        return responses