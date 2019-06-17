from request.models import *
#更新用例的步骤数
def updateStepCount(step_name):
    caseId=Step.objects.filter(step_name=step_name).values('case')[0]['case']
    stepCount = len(Step.objects.filter(case=caseId, status=1).values())
    Case.objects.filter(id=caseId).update(stepCount=stepCount)

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


#校验生成任务接口必须含有用例
def checkTask(case_ids):
    for caseId in case_ids:
        stepCount = Case.objects.filter(id=caseId).values('stepCount')[0]['stepCount']
        if stepCount == 0:
            return -1
    return 0