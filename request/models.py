from django.db import models
from django import forms
from django.contrib.auth.models import User

# Create your models here.
#测试环境表
class Environment(models.Model):
    env_ip=models.CharField(max_length=20)
    env_host = models.CharField(max_length=40)
    env_port = models.CharField(max_length=10)
    env_desc = models.CharField(max_length=100)

    def __str__(self):
        return self.env_ip

#开发数据库表
class Database(models.Model):
    db_type=models.CharField(max_length=4)
    db_typename=models.CharField(max_length=20,default="")
    db_name = models.CharField(max_length=100)
    db_ip = models.CharField(max_length=20)
    db_port = models.CharField(max_length=20)
    db_user = models.CharField(max_length=20)
    db_password = models.CharField(max_length=20)
    db_remark = models.CharField(max_length=100,default="")

    def __str__(self):
        return self.db_name

#开发NosqlDb表
class NosqlDb(models.Model):
    host = models.CharField(max_length=40)
    port = models.CharField(max_length=10)
    password = models.CharField(max_length=200)
    NosqlDb_desc = models.CharField(max_length=500)

    def __str__(self):
        return self.host

#邮件配置表
class Email(models.Model):
    sender=models.CharField(max_length=100)
    receivers = models.CharField(max_length=100)
    host_dir = models.CharField(max_length=100)
    email_port=models.CharField(max_length=20, default="")
    username = models.CharField(max_length=100)
    passwd = models.CharField(max_length=20)
    Headerfrom = models.CharField(max_length=100)
    Headerto = models.CharField(max_length=100)
    subject = models.CharField(max_length=100,default="")

    def __str__(self):
        return self.username

#项目表
class Project(models.Model):
    project_name=models.CharField(max_length=20,verbose_name="项目名")
    project_desc = models.CharField(max_length=200, blank=True, verbose_name="项目描述")
    status= models.BooleanField( verbose_name="状态")

    class Meta:
        verbose_name = '项目'
        verbose_name_plural = '项目'

    def __str__(self):
        return self.project_name




#模块表
class Modules(models.Model):
    Project = models.ForeignKey(Project, on_delete=models.CASCADE,verbose_name="项目名")
    Modules_name=models.CharField(max_length=20,verbose_name="模块名")
    Testers=models.ManyToManyField('auth.User',blank=True,verbose_name="测试人员")
    Developer = models.CharField(max_length=100,blank=True,verbose_name="开发人员")
    Modules_desc = models.CharField(max_length=200, blank=True, verbose_name="项目描述")
    status = models.BooleanField(verbose_name="状态")

    class Meta:
        verbose_name = '模块'
        verbose_name_plural = '模块'

    def __str__(self):
        return self.Modules_name

#用例表
class Case(models.Model):
    Modules=models.ForeignKey(Modules,on_delete=models.CASCADE)
    case_name = models.CharField(max_length=100)
    api = models.CharField(max_length=100)
    stepCount = models.IntegerField(default=0)
    status = models.BooleanField()
    version = models.CharField(max_length=20)
    case_weights = models.IntegerField(default=0)
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)
    case_desc = models.CharField(max_length=100,blank=True)

    def __str__(self):
        return self.case_name
#步骤表
class Step(models.Model):
    case=models.ForeignKey(Case,on_delete=models.CASCADE)
    step_name = models.CharField(max_length=100)
    step_desc = models.CharField(max_length=100)
    steplevel = models.CharField(max_length=10)
    method = models.CharField(max_length=10)
    params = models.CharField(max_length=500)
    headers = models.CharField(max_length=500)
    files = models.CharField(max_length=500)
    assert_response = models.CharField(max_length=4000)
    api_dependency = models.CharField(max_length=500,default="")
    step_weights = models.IntegerField(default=0)
    status = models.BooleanField()
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.step_name

#步骤依赖表
class Reference_step(models.Model):
    step=models.ForeignKey(Step,on_delete=models.CASCADE)
    step_name=models.CharField(max_length=100,default="")
    path = models.CharField(max_length=100, default="")
    reference_step_name = models.CharField(max_length=100,default="")
    variable = models.CharField(max_length=200)
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.step

#sql表
class Sql(models.Model):
    step=models.ForeignKey(Step,on_delete=models.CASCADE)
    db = models.CharField(max_length=40, default="")
    db_remark = models.CharField(max_length=100, default="")
    sql_condition = models.IntegerField()
    is_select = models.BooleanField()
    variable = models.CharField(max_length=200)
    sql = models.CharField(max_length=4000)
    remake = models.CharField(max_length=200)
    status = models.BooleanField()
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

# NoSql表
class NoSql(models.Model):
    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    Nosql_dataType = models.IntegerField()
    Nosql_condition = models.IntegerField()
    is_select = models.BooleanField()
    variable = models.CharField(max_length=200)
    Nosql = models.CharField(max_length=4000)
    remake = models.CharField(max_length=200)
    status = models.BooleanField()
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.Nosql

#任务表
class Task(models.Model):
    case=models.ForeignKey(Case,on_delete=models.CASCADE)
    task_name = models.CharField(max_length=200)
    task_run_time_regular = models.CharField(max_length=100)
    ip=models.CharField(max_length=40,default="")
    Nosqldb = models.CharField(max_length=40,default="")
    db = models.CharField(max_length=40,default="")
    email = models.CharField(max_length=40,default="")
    failcount = models.CharField(max_length=40,default="")
    remark = models.CharField(max_length=200)
    Nosqldb_desc = models.CharField(max_length=400,default="")
    db_remark = models.CharField(max_length=100, default="")
    env_desc = models.CharField(max_length=100, default="")
    subject = models.CharField(max_length=100, default="")
    status = models.BooleanField()
    carrystatus = models.IntegerField(default=2)
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.task_name

#测试结果表
class api_test_result(models.Model):
    task=models.ForeignKey(Task,on_delete=models.CASCADE)
    case = models.ForeignKey(Case,on_delete=models.CASCADE)
    step = models.ForeignKey(Step,on_delete=models.CASCADE)
    case_result = models.CharField(max_length=200)
    error_info = models.CharField(max_length=200)
    response_body = models.CharField(max_length=500)
    case_start_time = models.DateTimeField()
    case_end_time = models.DateTimeField()
    case_run_time = models.DateTimeField()
    def __str__(self):
        return self.case_result

#统计分析总表
#任务表
class StatisticsData(models.Model):
    casenumber = models.IntegerField()
    stepnumber = models.IntegerField()
    tasknumber = models.IntegerField()
    carrynumber = models.IntegerField()
    passnumber = models.IntegerField()
    asserterrornumber = models.IntegerField()
    failnumber = models.IntegerField()
    errorratio = models.IntegerField()
    def __str__(self):
        return self.casenumber

#邮件和日志的反馈
class LogAndHtmlfeedback(models.Model):
    test_step = models.CharField(max_length=100)
    test_status = models.IntegerField()
    test_response = models.CharField(max_length=500)
    test_carryTaskid = models.CharField(max_length=40,default="")
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

#第几次执行任务
class CarryTask(models.Model):
    task_name = models.CharField(max_length=200)
    htmlreport = models.CharField(max_length=200, default="")
    successlogname = models.CharField(max_length=200, default="")
    errorlogname = models.CharField(max_length=200, default="")
    stepcountall = models.IntegerField(default=0)
    stepcountnow = models.IntegerField(default=0)
    out_id = models.CharField(max_length=200, default="")
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.task_name

#添加用户表的另一个密码字段
pwd_field = models.CharField(max_length=30, default="")
pwd_field.contribute_to_class(User, 'pwd')
