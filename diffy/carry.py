import os
def start(candidate,master):
    #windows
    if os.name=="nt":
        command='''
        java -jar ./diffy/diffy-server.jar \
        -candidate='{candidate}' \
        -master.primary='{master}' \
        -master.secondary='{master}' \
        -service.protocol='http' \
        -serviceName='My Service' \
        -proxy.port=:8880 \
        -admin.port=:8881 \
        -http.port=:8888 \
        -rootUrl='localhost:8888' \
        -excludeHttpHeadersComparison=true \
        -allowHttpSideEffects=true   \
        '''.format(candidate=candidate,master=master)
        with open("run.sh","w",encoding="utf-8") as fp:
            fp.write(command)
        fp.close()
        os.system("run.sh start")
    #linux
    else:
        command = '''
            sudo nohup java -jar ./diffy/diffy-server.jar \
            -candidate='{candidate}' \
            -master.primary='{master}' \
            -master.secondary='{master}' \
            -service.protocol='http' \
            -serviceName='My Service' \
            -proxy.port=:8880 \
            -admin.port=:8881 \
            -http.port=:8888 \
            -rootUrl='localhost:8888' \
            -excludeHttpHeadersComparison=true \
            -allowHttpSideEffects=true  > nohup.out &\
            '''.format(candidate=candidate, master=master)
        os.system(command)

def shutdown(port):
    # windows
    if os.name == "nt":
        command='netstat -aon | findstr %s' % port
        pid = os.popen(command).read().split()[-1]
        if pid:
            killCommand = "taskkill -PID {pid} -F".format(pid=pid)
            os.popen(killCommand)
    # linux
    else:
        command="sudo lsof -i:"+str(port)+"|awk 'NR==2{print $2}'"
        pid = os.popen(command).read()[0:-1]
        if pid:
            killCommand = "sudo kill -9 {pid}".format(pid=pid)
            os.popen(killCommand)

#start("adhoc-query.k8s-new.qunhequnhe.com:80","adhoc-query.kube-aliyun.qunhequnhe.com:80")
#shutdown(8880)
#shutdown(8881)
