from public.request import *
#发送企信
def sendWechat(users,content,subject,url):
    #uri = "http://kaptain.qunhequnhe.com/api/wechat/sendHtmlCard?users={}&content={}&subject={}&url={}".format(users,content,subject,url)
    uri = "http://kaptain.qunhequnhe.com/api/wechat/sendHtmlCard"
    headers = {"kaptain-token":"1ae6dfff-fd2d-472e-aa69-e23bf0092c89","Content-Type":"application/json"}
    params = {"users":users,"content":content,"subject":subject,"url":url}
    http("postbody", uri, params, headers)