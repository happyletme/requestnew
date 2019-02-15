#-*-coding:utf-8-*-
import requests,json
from public.script_function import *
class Http:
    def __init__(self,model):
        self.model=model
    def __request(self,**kwargs):
        if self.model.lower() == "get":
            response = requests.request("get", kwargs["url"], params=kwargs["params"], headers=kwargs["headers"])
        # post的参数名要为data
        elif self.model.lower() == "put":
            # 转换成字符串传入
            params = json.dumps(kwargs["params"], ensure_ascii=False).encode()
            response = requests.request("put", kwargs["url"], data=params, headers=kwargs["headers"])
        elif self.model.lower() == "delete":
            # 转换成字符串传入
            params = json.dumps(kwargs["params"], ensure_ascii=False).encode()
            response = requests.request("delete", kwargs["url"], data=params, headers=kwargs["headers"])
        elif self.model.lower() == "postbody":
            # 转换成字符串传入
            params = json.dumps(kwargs["params"], ensure_ascii=False).encode()
            response = requests.request("post", kwargs["url"], data=params, headers=kwargs["headers"])
        elif self.model.lower() == "postform":
            response = requests.request("post", kwargs["url"], data=kwargs["params"], headers=kwargs["headers"])
        elif self.model.lower() == "postfile":
            response = requests.request("post", kwargs["url"], data=kwargs["params"], headers=kwargs["headers"],
                                        files=kwargs["files"])
        return response

    #文本转换成json字符串
    def __changeJson(self,response,**kwargs):
        try:
            responseJson = json.loads(response.text)
            return responseJson
        except:
            echo(kwargs["url"], self.model, kwargs["headers"], kwargs["params"],
                 '请求返回值为: ' + str(response.text))
            errormessage = '返回值非json格式'
            raise RuntimeError(errormessage)
    def __call__(self,fuc):
        def wrapper(*args,**kwargs):
            fuc(*args, **kwargs)
            response=self.__request(**kwargs)
            responseJson=self.__changeJson(response,**kwargs)
            return responseJson,response.status_code
        return wrapper

@Http(model="GET")
def get(url,params,headers):
    pass

@Http(model="PUT")
def put(url,params,headers):
    pass

@Http(model="DELETE")
def delete(url,params,headers):
    pass

@Http(model="POSTFORM")
def postform(url,params,headers):
    pass

@Http(model="POSTBODY")
def postbody(url,params,headers):
    pass

@Http(model="POSTFILE")
def postfile(url,params,headers,files):
    pass

