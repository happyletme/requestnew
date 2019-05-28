#!/usr/bin/env python
# -*- coding:utf8 -*-

import re
from public.expandfunction import Expandfunction
#输入字符串，执行函数，返回值替换原串
class Carryfunction(Expandfunction):
    def __init__(self):
        pass
    def carry_string(self,string):
        patternfunction = re.compile(r'\${__(.*?)}')  # 把函数给提取出来
        functionstrlist = patternfunction.findall(string)
        for functionstr in functionstrlist:
            patternSeparation = re.compile(r'(.*)?\((.*)?\)')  # 把函数名和参数剥离
            Separationfunctionstrlist = patternSeparation.findall(functionstr)
            functionname = Separationfunctionstrlist[0][0]

            # 生成函数
            func = getattr(self, functionname)
            functionparamslist = Separationfunctionstrlist[0][1].split(',')

            # 如果参数是字符串的去掉';如果是整数转换成整数
            changeregex = r"'"
            newfunctionparamslist = []
            for functionparams in functionparamslist:
                #有参数走正常
                try:
                    if len(re.findall(changeregex, functionparams)) == 0:
                        functionparams = eval(functionparams)
                    else:
                        functionparams = re.sub(changeregex, "", functionparams)
                    newfunctionparamslist.append(functionparams)
                except:
                    newfunctionparamslist=[]
            result = func(*newfunctionparamslist)

            # 替换原先的字符串
            regex = r"\${__" + functionname + r"\(" + Separationfunctionstrlist[0][1] + r"\)}"
            string = re.sub(regex, str(result), string)
            try:
                patternSeparation = re.compile(r'(.*)?\((.*)?\)')  # 把函数名和参数剥离
                Separationfunctionstrlist = patternSeparation.findall(functionstr)
                functionname = Separationfunctionstrlist[0][0]

                # 生成函数
                print (functionname)
                func = getattr(self, functionname)
                functionparamslist = Separationfunctionstrlist[0][1].split(',')


                # 如果参数是字符串的去掉';如果是整数转换成整数
                changeregex = r"'"
                newfunctionparamslist = []
                for functionparams in functionparamslist:
                    if len(re.findall(changeregex, functionparams)) == 0:
                        functionparams = eval(functionparams)
                    else:
                        functionparams = re.sub(changeregex, "", functionparams)
                    newfunctionparamslist.append(functionparams)
                result = func(*newfunctionparamslist)

                # 替换原先的字符串
                regex = r"\${__" + functionname + r"\(" + Separationfunctionstrlist[0][1] + r"\)}"
                string = re.sub(regex, str(result), string)
            except:
                # 如果里面有变量的时候，阻塞住
                pass
        return string
carryfunction=Carryfunction()
#将文件的全局变量通过类属性传递给脚本文件
class Transferfunction:
    def __init__(self):
        self.carryfunction=carryfunction