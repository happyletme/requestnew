import pandas
def convertToHtml(result,title):
    #将数据转换为html的table
    #result是list[list1,list2]这样的结构
    #title是list结构；和result一一对应。titleList[0]对应resultList[0]这样的一条数据对应html表格中的一列
    d = {}
    index = 0
    for t in title:
        d[t]=result[index]
        index = index+1
    df = pandas.DataFrame(d)
    df = df[title]
    h = df.to_html(index=False)
    return h

def makeEamilBody(result,title,task_name,env_desc,nosqldb_desc=""):
    bodyTable=convertToHtml(result, title)
    body =\
        '''
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>邮件报告</title>
</head>
<body>
    <h1>邮件报告</h1>
    <p>执行任务名：'''+task_name+'''</p>
    <p>访问地址名称：'''+env_desc+'''</p>
    <p>Nosql数据库名称：'''+nosqldb_desc+'''</p>
    '''+bodyTable+'''
</body>
</html>
    '''
    return body
