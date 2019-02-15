from request import sched
from public.run import *
from request.models import *
from request.models import Database as Db
from public.sqldb import Database as sqldbDatabase
from public.sqldb import *
from public.redis import Redis
import json,requests,base64
from http.cookiejar import CookieJar

class Job:
    def __init__(self,taskname,schedule):
        self.taskname=taskname
        self.schedule=schedule
    #把时间表做数据处理
    def __get_date(self):
        self.task_schedule = self.schedule.split(' ')
        for i in range(len(self.task_schedule)):
            if self.task_schedule[i]=='*':
                self.task_schedule[i]=None

    # 启动数据库和启动IP
    def __get_ip_database(self,request, env_desc,nosqldb_desc, subject):
        # 环境
        env_list = Environment.objects.filter(env_desc=env_desc).values("env_ip", "env_host", "env_port")
        if env_list[0]['env_ip'] != "":
            if env_list[0]['env_port']!="":
                env_ip = "http://{host}:{port}".format(host=env_list[0]['env_ip'], port=env_list[0]['env_port'])
            else:
                env_ip = "http://{host}".format(host=env_list[0]['env_ip'])
        else:
            if env_list[0]['env_port'] != "":
                env_ip = "http://{host}:{port}".format(host=env_list[0]['env_host'], port=env_list[0]['env_port'])
            else:
                env_ip = "http://{host}".format(host=env_list[0]['env_host'])
        # Nosql数据库
        if nosqldb_desc == "":
            redis = None
        else:
            NosqlDbresult = NosqlDb.objects.filter(NosqlDb_desc=nosqldb_desc).values("host", "port", "password")
            host = NosqlDbresult[0]['host']
            if NosqlDbresult[0]['port'] == "":
                port = 6379
            else:
                port = NosqlDbresult[0]['port']
            if NosqlDbresult[0]['password'] == "":
                password = None
            else:
                password = NosqlDbresult[0]['password']
            redis = Redis(host, port, password)

        # 需要启动的开发数据库
        db = {}
        db_list = []
        task_data = Task.objects.filter(task_name=self.taskname).values('db')
        dbstr = task_data[0]['db']
        db_list = dbstr.split(',')
        if db_list!=['']:
            for i in db_list:
                data_list = Db.objects.filter(id=i).values("db_type", "db_ip", "db_port", "db_user", "db_password",
                                                           "db_name")
                # mysql
                if data_list[0]['db_type'] == '0':
                    databaseobj = sqldbDatabase(data_list[0]['db_ip'], data_list[0]['db_port'], data_list[0]['db_user'],
                                                data_list[0]['db_password'], data_list[0]['db_name'])
                # sql server
                else:
                    databaseobj = sqldbDatabase(data_list[0]['db_ip'], data_list[0]['db_user'],
                                                data_list[0]['db_password'],
                                                data_list[0]['db_name'])
                db[i] = databaseobj
        else:
            db=None

        create_db(db, env_ip,redis)

        #邮件
        # 如果要发送邮件拿到邮件配置数据
        if subject != None and subject!="":
            email_data = \
            Email.objects.filter(subject=subject).values('id', 'sender', 'receivers', 'host_dir', 'email_port',
                                                         'username', 'passwd', 'Headerfrom', 'Headerto', 'subject')[0]
            # 邮箱密码解密
            email_data['passwd'] = base64.b64decode(email_data['passwd']).decode()
        else:
            email_data = None
        return email_data
    #添加定时任务
    def create_job(self,request,env_desc,Nosqldb_desc,failcount,subject):
        self.__get_date()

        @sched.scheduled_job('cron', minute = self.task_schedule[0],hour = self.task_schedule[1], day  = self.task_schedule[2],month  = self.task_schedule[3], week   = self.task_schedule[4],id=self.taskname)
        def task():
            #启动数据库和启动IP和获取邮件配置数据
            email_data=self.__get_ip_database(request, env_desc,Nosqldb_desc,subject)
            interface(self.taskname,failcount,email_data)

    #删除定时任务
    def delete_job(self):
        try:
            #如果有任务删除任务
            sched.remove_job(self.taskname)
        except:
            #没有任务就跳过
            pass

    #添加单次任务
    def create_one_job(self,request,env_desc,Nosqldb_desc,failcount,subject):
        nowtime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        @sched.scheduled_job('date', run_date=nowtime,id="1")
        def task():
            #启动数据库和启动IP和获取邮件配置数据
            email_data=self.__get_ip_database(request, env_desc,Nosqldb_desc,subject)
            interface(self.taskname,failcount,email_data)











