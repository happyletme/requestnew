#-*-utf-8-*-
import os,shutil,socket
#判断一个夹是否存在，不存在创建
def create_dir(dir):
    isexist = os.path.isdir(dir)
    if not isexist:
        os.mkdir(dir)
    else:
        pass

#判断是否存在一个文件，如果存在先删除
def rm_file(name):
    if os.path.exists(name):
        os.remove(name)

#创建一个文件
def create_file(filename):
    with open(filename,"w") as fp:
        fp.close()

#获取本机ip
def getLocalIp():
    # 获取本机电脑名
    myname = socket.getfqdn(socket.gethostname())
    # 获取本机ip
    myaddr = socket.gethostbyname(myname)
    return myaddr
