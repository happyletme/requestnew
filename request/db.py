from request.models import *
#更新用例的步骤数
def updateStepCount(case):
    stepCount = len(Step.objects.filter(case=case, status=1).values())
    Case.objects.filter(case_name=case).update(stepCount=stepCount)

#更新步骤的sql数
def updateSqlCount(step):
    sqlCount = len(Sql.objects.filter(step=step, status=1).values())
    Step.objects.filter(step_name=step).update(sqlCount=sqlCount)


#更新步骤的noSql数
def updateNoSqlCount(step):
    nosqlCount = len(NoSql.objects.filter(step=step, status=1).values())
    Step.objects.filter(step_name=step).update(nosqlCount=nosqlCount)

#更新删除的用例步骤数
def updateDeleteStepCount(idstring):
    stepCountDic={}
    #将删除的用例ID和删除后预计剩下的用例数放入字典
    stepList = Step.objects.extra(where=['id IN (' + idstring + ')'])
    for step_name in stepList:
        caseId = Step.objects.filter(step_name=step_name).values('case')[0]['case']
        stepCount = len(Step.objects.filter(case=caseId, status=1).values())
        if caseId in stepCountDic.keys():
            stepCountDic[caseId] -= 1
        else:
            stepCountDic[caseId] = stepCount - 1

    #跟着用例数
    for caseId in stepCountDic.keys():
        Case.objects.filter(id=caseId).update(stepCount=stepCountDic[caseId])

#更新删除的步骤sql数
def updateDeleteSqlCount(idstring):
    sqlCountDic={}
    #将删除的步骤名字和删除后预计剩下的sql数放入字典
    sqlList = Sql.objects.extra(where=['id IN (' + idstring + ')'])

    for sql in sqlList:
        sqlCount = len(Sql.objects.filter(step=sql.step, status=1).values())
        if sql.step in sqlCountDic.keys():
            sqlCountDic[sql.step] -= 1
        else:
            sqlCountDic[sql.step] = sqlCount - 1

    #跟着用例数
    for step in sqlCountDic.keys():
        Step.objects.filter(step_name=step).update(sqlCount=sqlCountDic[step])

#更新删除的步骤Nosql数
def updateDeletenoSqlCount(idstring):
    nosqlCountDic={}
    #将删除的步骤名字和删除后预计剩下的nosql数放入字典
    nosqlList = NoSql.objects.extra(where=['id IN (' + idstring + ')'])

    for nosql in nosqlList:
        nosqlCount = len(NoSql.objects.filter(step=nosql.step, status=1).values())
        if nosql.step in nosqlCountDic.keys():
            nosqlCountDic[nosql.step] -= 1
        else:
            nosqlCountDic[nosql.step] = nosqlCount - 1

    #跟着用例数
    for step in nosqlCountDic.keys():
        Step.objects.filter(step_name=step).update(nosqlCount=nosqlCountDic[step])

#校验生成任务接口必须含有用例
def checkTask(case_ids):
    for caseId in case_ids:
        stepCount = Case.objects.filter(id=caseId).values('stepCount')[0]['stepCount']
        if stepCount == 0:
            return -1
    return 0