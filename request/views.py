from django.shortcuts import render
from django.shortcuts import HttpResponse,HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from request.models import *
from request.models import Database as Db
from django.db.models import Q
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.http import JsonResponse
from public.request import *
from public.system import *
from public.make_testcase import Make_testcase
from public.run import interface
from public.sqldb import create_db
from public.redis import Redis
from public.suit import Suit
import json,re,os,shutil,math,base64,uuid
#from request import sched
from public.job import Job
from public.sqldb import Database as sqldbDatabase
from public.request import *
from http.cookiejar import CookieJar
from decimal import Decimal
from django.utils.timezone import now, timedelta
from django.db.models import Min,Avg,Max,Sum
from django.apps import apps
from threading import Thread
from request import db


# Create your views here.
#分页显示数
NumberColumns=15

#当页面编辑新增删除后拿的全部数据，返回第一页的数据
def get_firstPage(dataModel):
    data_list = dataModel.objects.all().order_by("-id")
    paginator = Paginator(data_list, NumberColumns)
    contacts = paginator.page(1)
    return contacts

#当页面编辑新增删除后拿的全部数据，返回第一页的数据，根据登录用户过滤数据
def get_firstPagefiliterdata(dataModel,filiterdata):
    data_list = dataModel.objects.all().order_by("-id")
    #将数据再根据登录用户过滤一层
    if dataModel==Case:
        data_list = data_list.filter(Modules__in=filiterdata)
    elif dataModel==Modules:
        data_list = data_list.filter(id__in=filiterdata)
    elif dataModel == Step:
        data_list = data_list.filter(case__in=filiterdata)
    elif dataModel == Sql:
        data_list = data_list.filter(step__in=filiterdata)
    elif dataModel == NoSql:
        data_list = data_list.filter(step__in=filiterdata)
    paginator = Paginator(data_list, NumberColumns)
    contacts = paginator.page(1)
    return contacts

def get_index(request):
    return render(request,"index.html")

def login_action(request):
    if request.method=="POST":
        Username=request.POST.get("form-username")
        Password = request.POST.get("form-password")
        user=auth.authenticate(username=Username,password=Password)
        if user != None:
            auth.login(request,user)
            request.session["Username"]=Username
            User.objects.filter(username=Username).update(pwd=base64.b64encode(bytes(Password, 'utf-8')).decode())
            return HttpResponseRedirect("/first_page/")
        else:
            return render(request,"index.html",{"error":"Username and Password is error"})
@login_required
def first_page(request):
    try:
        Username=request.session["Username"]
        return render(request,"first_page.html",{"Username":Username})
    except:
        return render(request, "index.html")
#环境配置
@login_required
def env(request):
    env_ip = request.GET.get("ip")
    #print (env_ip)
    env_host = request.GET.get("host")
    env_port = request.GET.get("port")

    checkedenv_ids = request.GET.get("checkedenv_ids")
    try:
        env_list = Environment.objects.filter(Q(env_ip__contains=env_ip), Q(env_host__contains=env_host),Q(env_port__contains=env_port)).order_by("-id")
    except:
        env_list=Environment.objects.all().order_by("-id")
    paginator=Paginator(env_list,NumberColumns)
    page=request.GET.get("page")
    try:
        contacts=paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts=paginator.page(paginator.num_pages)
    response={"envs":contacts}
    if env_ip!=None:
        response["env_ip"]=env_ip
    if env_host!=None:
        response["env_host"]=env_host
    if env_port!=None:
        response["env_port"]=env_port
    if checkedenv_ids!=None:
        response["checkedenv_ids"] = checkedenv_ids
    else:
        response["checkedenv_ids"]=None
    return render(request, "./main/env.html",response)

@login_required
def env_add_data(request):
    env_ip=request.POST.get("ip")
    env_host=request.POST.get("host")
    env_port=request.POST.get("port")
    env_desc=request.POST.get("desc")
    code = len(Environment.objects.filter(env_desc=env_desc).values())
    # 不重复则新增数据
    if code == 0:
        Environment.objects.create(env_ip=env_ip,env_host=env_host,env_port=env_port,env_desc=env_desc)
        codeMessage =""
    # 重复则不新增数据
    else:
        codeMessage="访问地址名称重复，新增失败"
    contacts=get_firstPage(Environment)
    return render(request, "./main/env.html", {"envs": contacts,"code":code,"codeMessage":codeMessage})

@login_required
def env_edit_data(request):
    env_id = request.POST.get("id")
    env_ip=request.POST.get("ip")
    env_host=request.POST.get("host")
    env_port=request.POST.get("port")
    env_desc=request.POST.get("desc")
    code = len(Environment.objects.filter(~Q(id=env_id),env_desc=env_desc).values())
    # 不重复则更新数据
    if code == 0:
        Environment.objects.filter(id=env_id).update(env_ip=env_ip, env_host=env_host, env_port=env_port,
                                                     env_desc=env_desc)
        codeMessage = ""
    # 重复则不更新数据
    else:
        codeMessage = "访问地址名称重复，修改失败"
    contacts = get_firstPage(Environment)
    return render(request, "./main/env.html", {"envs": contacts,"code":code,"codeMessage":codeMessage})

@login_required
def env_delete_data(request):
    env_ids = request.POST.get("id")
    env_ids = env_ids.split(',')
    # 第一个传过来的值为None字符串 不需要
    env_ids = env_ids[1:]

    # 批量删除
    idstring = ','.join(env_ids)
    Environment.objects.extra(where=['id IN (' + idstring + ')']).delete()

    contacts = get_firstPage(Environment)
    return render(request, "./main/env.html", {"envs": contacts})

@login_required
def env_search_name(request):
    env_ip = request.GET.get("ip")
    env_host = request.GET.get("host")
    env_port = request.GET.get("port")
    env_list = Environment.objects.filter(Q(env_ip__contains=env_ip) , Q(env_host__contains=env_host) , Q(env_port__contains=env_port)).order_by("-id")
    paginator = Paginator(env_list, NumberColumns)
    contacts = paginator.page(1)
    return render(request, "./main/env.html", {"envs": contacts,"env_ip":env_ip,"env_host":env_host,"env_port":env_port})

#邮箱配置

@login_required
def email(request):
    email_receivers = request.GET.get("receivers")
    email_username = request.GET.get("username")
    email_subject = request.GET.get("subject")
    checkedenv_ids = request.GET.get("checkedenv_ids")
    try:
        email_list = Email.objects.filter(Q(subject__contains=email_subject), Q(username__contains=email_username),Q(receivers__contains=email_receivers)).order_by("-id")
    except:
        email_list=Email.objects.all().order_by("-id")
    paginator=Paginator(email_list,NumberColumns)
    page=request.GET.get("page")
    try:
        contacts=paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts=paginator.page(paginator.num_pages)
    response={"emails":contacts}
    if email_receivers!=None:
        response["email_receivers"]=email_receivers
    if email_username!=None:
        response["email_username"]=email_username
    if email_subject!=None:
        response["email_subject"]=email_subject
    if checkedenv_ids!=None:
        response["checkedenv_ids"] = checkedenv_ids
    else:
        response["checkedenv_ids"]=None
    return render(request, "./main/email.html",response)

@login_required
def email_add_data(request):
    email_sender=request.POST.get("sender")
    email_receivers=request.POST.get("receivers")
    email_host_dir=request.POST.get("host_dir")
    email_port=request.POST.get("email_port")
    email_username=request.POST.get("username")
    email_passwd = request.POST.get("passwd")
    email_Headerfrom = request.POST.get("Headerfrom")
    email_Headerto = request.POST.get("Headerto")
    email_subject = request.POST.get("subject")
    code = len(Email.objects.filter(subject=email_subject).values())
    # 不重复则新增数据
    if code == 0:
        encryptionEmail_passwd = base64.b64encode(bytes(email_passwd, 'utf-8')).decode()
        Email.objects.create(sender=email_sender,receivers=email_receivers,host_dir=email_host_dir,email_port=email_port,username=email_username, \
                                   passwd=encryptionEmail_passwd, Headerfrom=email_Headerfrom, Headerto=email_Headerto,subject=email_subject)
        codeMessage = ""
    # 重复则不新增数据
    else:
        codeMessage = "邮件标题重复，新增失败"
    contacts = get_firstPage(Email)
    return render(request, "./main/email.html", {"emails": contacts,"code":code,"codeMessage":codeMessage})

@login_required
def email_edit_data(request):
    email_id = request.POST.get("id")
    email_sender = request.POST.get("sender")
    email_receivers = request.POST.get("receivers")
    email_host_dir = request.POST.get("host_dir")
    email_port = request.POST.get("email_port")
    email_username = request.POST.get("username")
    email_passwd = request.POST.get("passwd")
    email_Headerfrom = request.POST.get("Headerfrom")
    email_Headerto = request.POST.get("Headerto")
    email_subject = request.POST.get("subject")

    code = len(Email.objects.filter(~Q(id=email_id), subject=email_subject).values())
    # 不重复则更新数据
    if code == 0:
        # 先去数据库中获取密码比对，若一致不修改
        oldEmail_passwd = Email.objects.filter(id=email_id).values('passwd')
        if oldEmail_passwd[0]['passwd'] != email_passwd:
            # 修改密码
            encryptionEmail_passwd = base64.b64encode(bytes(email_passwd, 'utf-8')).decode()
            Email.objects.filter(id=email_id).update(sender=email_sender, receivers=email_receivers,
                                                     host_dir=email_host_dir, email_port=email_port,
                                                     username=email_username, \
                                                     passwd=encryptionEmail_passwd, Headerfrom=email_Headerfrom,
                                                     Headerto=email_Headerto, subject=email_subject)
        else:
            Email.objects.filter(id=email_id).update(sender=email_sender, receivers=email_receivers,
                                                     host_dir=email_host_dir, email_port=email_port,
                                                     username=email_username, \
                                                     Headerfrom=email_Headerfrom, Headerto=email_Headerto,
                                                     subject=email_subject)
        codeMessage = ""
    # 重复则不更新数据
    else:
        codeMessage = "邮件标题重复，修改失败"

    contacts = get_firstPage(Email)
    return render(request, "./main/email.html", {"emails": contacts,"code":code,"codeMessage":codeMessage})

@login_required
def email_delete_data(request):
    email_ids = request.POST.get("id")
    email_ids=email_ids.split(',')
    # 第一个传过来的值为None字符串 不需要
    email_ids = email_ids[1:]

    # 批量删除
    idstring = ','.join(email_ids)
    Email.objects.extra(where=['id IN (' + idstring + ')']).delete()

    contacts = get_firstPage(Email)
    return render(request, "./main/email.html", {"emails": contacts})

@login_required
def email_search_name(request):
    email_receivers = request.GET.get("receivers")
    email_username = request.GET.get("username")
    email_subject = request.GET.get("subject")
    email_list = Email.objects.filter(Q(subject__contains=email_subject), Q(username__contains=email_username),
                                      Q(receivers__contains=email_receivers)).order_by("-id")
    paginator = Paginator(email_list, NumberColumns)
    contacts = paginator.page(1)
    return render(request, "./main/email.html", {"emails": contacts,"email_receivers":email_receivers,\
                                                 "email_username":email_username,"email_subject":email_subject})

#数据库配置

@login_required
def database(request):
    db_ip = request.GET.get("db_ip")
    db_name = request.GET.get("db_name")
    db_typename = request.GET.get("db_typename")
    checkedenv_ids = request.GET.get("checkedenv_ids")
    try:
        database_list = Db.objects.filter(Q(db_ip__contains=db_ip), Q(db_name__contains=db_name),Q(db_typename__contains=db_typename)).order_by("-id")
    except:
        database_list=Db.objects.all().order_by("-id")
    paginator=Paginator(database_list,NumberColumns)
    page=request.GET.get("page")
    try:
        contacts=paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts=paginator.page(paginator.num_pages)
    response={"databases":contacts}
    if db_ip!=None:
        response["db_ip"]=db_ip
    if db_name!=None:
        response["db_name"]=db_name
    if db_typename!=None:
        response["db_typename"]=db_typename
    if checkedenv_ids!=None:
        response["checkedenv_ids"] = checkedenv_ids
    else:
        response["checkedenv_ids"]=None
    return render(request, "./main/database.html",response)

@login_required
def database_add_data(request):
    db_typename=request.POST.get("db_type")
    db_name=request.POST.get("db_name")
    db_ip=request.POST.get("db_ip")
    db_port=request.POST.get("db_port")
    db_user = request.POST.get("db_user")
    db_password = request.POST.get("db_password")
    db_remark = request.POST.get("db_remark")
    code = len(Db.objects.filter(db_remark=db_remark).values())
    # 不重复则新增数据
    if code == 0:
        if db_typename=="Mysql":
            Db.objects.create(db_type=0,db_typename=db_typename,db_name=db_name,db_ip=db_ip,db_port=db_port,\
                                    db_user=db_user,db_password=db_password,db_remark=db_remark)
        elif db_typename=="SqlServer":
            Db.objects.create(db_type=1,db_typename=db_typename,db_name=db_name,db_ip=db_ip,db_user=db_user,\
                                    db_password=db_password,db_remark=db_remark)
        codeMessage = ""
    # 重复则不新增数据
    else:
        codeMessage = "数据库的连接名称重复，新增失败"
    contacts = get_firstPage(Db)
    return render(request, "./main/database.html", {"databases": contacts,"code":code,"codeMessage":codeMessage})
@login_required
def database_edit_data(request):
    db_id = request.POST.get("id")
    db_typename = request.POST.get("db_type")
    db_name = request.POST.get("db_name")
    db_ip = request.POST.get("db_ip")
    db_port = request.POST.get("db_port")
    db_user = request.POST.get("db_user")
    db_password = request.POST.get("db_password")
    db_remark = request.POST.get("db_remark")
    code = len(Db.objects.filter(~Q(id=db_id), db_remark=db_remark).values())
    if code == 0:
        old_db_remark=Db.objects.filter(id=db_id).values('db_remark')[0]['db_remark']
        if db_typename == "Mysql":
            Db.objects.filter(id=db_id).update(db_type=0, db_typename=db_typename, db_name=db_name, db_ip=db_ip,
                                               db_port=db_port, \
                                               db_user=db_user, db_password=db_password, db_remark=db_remark)
        elif db_typename == "SqlServer":
            Db.objects.filter(id=db_id).update(db_type=1, db_typename=db_typename, db_name=db_name, db_ip=db_ip,
                                               db_port="", \
                                               db_user=db_user, db_password=db_password, db_remark=db_remark)
        #监控若修改了数据库的连接名，则变更sql表的数据库字段
        if old_db_remark!=db_remark:
            Sql.objects.filter(db=db_id).update(db_remark=db_remark)
        codeMessage = ""
    # 重复则不更新数据
    else:
        codeMessage = "数据库的连接名称重复，修改失败"
    contacts = get_firstPage(Db)
    return render(request, "./main/database.html", {"databases": contacts,"code":code,"codeMessage":codeMessage})

@login_required
def database_delete_data(request):
    database_ids = request.POST.get("id")
    database_ids=database_ids.split(',')
    for database_id in database_ids:
        if database_id!="":
            Db.objects.filter(id=database_id).delete()
    contacts = get_firstPage(Db)
    return render(request, "./main/database.html", {"databases": contacts})

@login_required
def database_search_name(request):
    db_ip = request.GET.get("db_ip")
    db_name = request.GET.get("db_name")
    db_typename = request.GET.get("db_typename")
    database_list = Db.objects.filter(Q(db_ip__contains=db_ip), Q(db_name__contains=db_name),
                                            Q(db_typename__contains=db_typename)).order_by("-id")
    paginator = Paginator(database_list, NumberColumns)
    contacts = paginator.page(1)
    return render(request, "./main/database.html", {"databases": contacts,"db_ip":db_ip,\
                                                 "db_name":db_name,"db_typename":db_typename})

#NoSqlDB配置
@login_required
def NosqlDatabase(request):
    host = request.GET.get("host")
    port = request.GET.get("port")

    checkedenv_ids = request.GET.get("checkedenv_ids")
    try:
        NosqlDb_list = NosqlDb.objects.filter( Q(env_host__contains=host),Q(env_port__contains=port)).order_by("-id")
    except:
        NosqlDb_list=NosqlDb.objects.all().order_by("-id")
    paginator=Paginator(NosqlDb_list,NumberColumns)
    page=request.GET.get("page")
    try:
        contacts=paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts=paginator.page(paginator.num_pages)
    response={"NosqlDbs":contacts}
    if host!=None:
        response["host"]=host
    if port!=None:
        response["port"]=port
    if checkedenv_ids!=None:
        response["checkedenv_ids"] = checkedenv_ids
    else:
        response["checkedenv_ids"]=None
    return render(request, "./main/NosqlDb.html",response)

@login_required
def NosqlDatabase_add_data(request):
    host=request.POST.get("host")
    port=request.POST.get("port")
    NosqlDb_desc=request.POST.get("desc")
    password = request.POST.get("password")
    code = len(NosqlDb.objects.filter(NosqlDb_desc=NosqlDb_desc).values())
    # 不重复则新增数据
    if code == 0:
        NosqlDb.objects.create(password=password,host=host,port=port,NosqlDb_desc=NosqlDb_desc)
        codeMessage =""
    # 重复则不新增数据
    else:
        codeMessage="NosqlDb名称重复，新增失败"
    contacts=get_firstPage(NosqlDb)
    return render(request, "./main/NosqlDb.html", {"NosqlDbs": contacts,"code":code,"codeMessage":codeMessage})

@login_required
def NosqlDatabase_edit_data(request):
    id = request.POST.get("id")
    host=request.POST.get("host")
    port=request.POST.get("port")
    desc=request.POST.get("desc")
    code = len(NosqlDb.objects.filter(~Q(id=id),NosqlDb_desc=desc).values())
    # 不重复则更新数据
    if code == 0:
        NosqlDb.objects.filter(id=id).update(host=host, port=port,
                                             NosqlDb_desc=desc)
        codeMessage = ""
    # 重复则不更新数据
    else:
        codeMessage = "NosqlDb名称重复，修改失败"
    contacts = get_firstPage(NosqlDb)
    return render(request, "./main/NosqlDb.html", {"NosqlDbs": contacts,"code":code,"codeMessage":codeMessage})

@login_required
def NosqlDatabase_delete_data(request):
    env_ids = request.POST.get("id")
    env_ids = env_ids.split(',')
    # 第一个传过来的值为None字符串 不需要
    env_ids = env_ids[1:]

    # 批量删除
    idstring = ','.join(env_ids)
    NosqlDb.objects.extra(where=['id IN (' + idstring + ')']).delete()

    contacts = get_firstPage(NosqlDb)
    return render(request, "./main/NosqlDb.html", {"NosqlDbs": contacts})

@login_required
def NosqlDatabase_search_name(request):
    host = request.GET.get("host")
    port = request.GET.get("port")
    NosqlDb_list = NosqlDb.objects.filter( Q(host__contains=host) , Q(port__contains=port)).order_by("-id")
    paginator = Paginator(NosqlDb_list, NumberColumns)
    contacts = paginator.page(1)
    return render(request, "./main/NosqlDb.html", {"NosqlDbs": contacts,"host":host,"port":port})

#测试项目
@login_required
def project(request):
    project_name = request.GET.get("project_name")
    select = request.GET.get("select")
    checkedenv_ids = request.GET.get("checkedenv_ids")
    try:
        if select != '2':
            project_list = Project.objects.filter(Q(project_name__contains=project_name), Q(status=select)).order_by("-id")
        else:
            project_list = Project.objects.filter(Q(project_name__contains=project_name)).order_by("-id")
    except:
        project_list=Project.objects.all().order_by("-id")
    paginator=Paginator(project_list,NumberColumns)
    page=request.GET.get("page")
    try:
        contacts=paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts=paginator.page(paginator.num_pages)
    response={"projects":contacts}
    if project_name!=None:
        response["project_name"]=project_name
    if select!=None:
        response["select"]=select
    else:
        select = '2'
        response["select"] = select
    if checkedenv_ids!=None:
        response["checkedenv_ids"] = checkedenv_ids
    else:
        response["checkedenv_ids"]=None
    return render(request, "./main/project.html",response)
@login_required
def project_add_data(request):
    project_name=request.POST.get("project_name")
    project_desc=request.POST.get("project_desc")
    testers = request.POST.get("testers")
    developer = request.POST.get("developer")
    status = request.POST.get("status")
    code=len(Project.objects.filter(project_name=project_name).values())
    #不重复则新增数据
    if code==0:
        if status!=None:
            Project.objects.create(project_name=project_name,project_desc=project_desc,Testers=testers,Developer=developer,status=1)
        else:
            Project.objects.create(project_name=project_name, project_desc=project_desc, Testers=testers,
                               Developer=developer, status=0)
        codeMessage = ""
    # 重复则不新增数据
    else:
        codeMessage = "项目名重复，新增失败"
    contacts = get_firstPage(Project)
    return render(request, "./main/project.html", {"projects": contacts,"select":'2',"code":code,"codeMessage":codeMessage})

@login_required
def project_edit_data(request):
    project_id = request.POST.get("id")
    project_name = request.POST.get("project_name")
    project_desc = request.POST.get("project_desc")
    testers = request.POST.get("testers")
    developer = request.POST.get("developer")
    status = request.POST.get("status")
    code = len(Project.objects.filter(~Q(id=project_id), project_name=project_name).values())
    # 不重复则更新数据
    if code == 0:
        if status != None:
            Project.objects.filter(id=project_id).update(project_name=project_name, project_desc=project_desc,
                                                         Testers=testers, Developer=developer, status=1)
        else:
            Project.objects.filter(id=project_id).update(project_name=project_name, project_desc=project_desc,
                                                         Testers=testers, Developer=developer, status=0)
        codeMessage = ""
    # 重复则不更新数据
    else:
        codeMessage = "项目名重复，编辑失败"
    contacts = get_firstPage(Project)
    return render(request, "./main/project.html", {"projects": contacts,"select":'2',"code":code,"codeMessage":codeMessage})

@login_required
def project_delete_data(request):
    project_ids = request.POST.get("id")
    project_ids=project_ids.split(',')
    # 第一个传过来的值为None字符串 不需要
    project_ids = project_ids[1:]

    # 批量删除
    idstring = ','.join(project_ids)
    Project.objects.extra(where=['id IN (' + idstring + ')']).delete()

    contacts = get_firstPage(Project)
    return render(request, "./main/project.html", {"projects": contacts,"select":'2'})

@login_required
def project_search_name(request):
    project_name = request.GET.get("project_name")
    select = request.GET.get("select")
    if select!='2':
        project_list = Project.objects.filter(Q(project_name__contains=project_name),Q(status=select)).order_by("-id")
    else:
        project_list = Project.objects.filter(Q(project_name__contains=project_name)).order_by("-id")
    paginator = Paginator(project_list, NumberColumns)
    contacts = paginator.page(1)
    return render(request, "./main/project.html", {"projects": contacts,"project_name":project_name,\
                                                   "select":select})


#测试模块
#把测试项目的project_name取出，当成新增编辑页面项目的可选的列
def get_project_name(filiterdata):
    project_names = set()
    for filiter in filiterdata:
        if filiter.Project.status:
            project_names.add(filiter.Project.project_name)
    project_names=list(project_names)
    return project_names

#把测试人员取出
def get_testers(modules_list):
    testers_list = []
    for module in modules_list.order_by("-id"):
        testers = ""
        count = 0
        for tester in module.Testers.all():
            if count == 0:
                testers += str(tester)
            else:
                testers += "," + str(tester)
            count += 1
        testers_list.append(testers)
    return testers_list
@login_required
def modules(request):
    modules_name=request.GET.get("modules_name")
    project_name = request.GET.get("project_name")
    Developer = request.GET.get("Developer")
    select = request.GET.get("select")
    checkedenv_ids = request.GET.get("checkedenv_ids")
    try:
        if project_name == "0":
            if select != '2':
                modules_list = Modules.objects.filter(Q(Modules_name__contains=modules_name),
                                                      Q(Developer__contains=Developer), Q(status=select)).order_by("-id")
            else:
                modules_list = Modules.objects.filter(Q(Modules_name__contains=modules_name),
                                                      Q(Developer__contains=Developer)).order_by("-id")
        else:
            # 得到外键数据
            project = Project.objects.get(project_name=project_name)
            if select != '2':
                modules_list = Modules.objects.filter(Q(Modules_name__contains=modules_name),
                                                      Q(Developer__contains=Developer), Q(status=select),
                                                      Q(Project=project)).order_by("-id")
            else:
                modules_list = Modules.objects.filter(Q(Modules_name__contains=modules_name),
                                                      Q(Developer__contains=Developer), Q(Project=project)).order_by("-id")
    except:
        modules_list=Modules.objects.all().order_by("-id")

    # 根据用户过滤数据权限
    filiterdata = get_filiterdata(request)
    modules_list = modules_list.filter(id__in=filiterdata)

    # 获取测试人员名称
    testers_list = get_testers(modules_list)

    paginator=Paginator(modules_list,NumberColumns)
    page=request.GET.get("page")
    try:
        contacts=paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts=paginator.page(paginator.num_pages)

    #将模块数据和测试人员打包
    contactszip=zip(contacts,testers_list)

    response={"modules":contactszip,"modulees":contacts}
    project_names = get_project_name(filiterdata)
    if modules_name!=None:
        response["modules_name"]=modules_name
    if Developer!=None:
        response["Developer"]=Developer
    if project_names!=None:
        response["project_names"]=project_names
    if project_name!=None:
        response["selectproject"]=project_name
    else:
        project_name = '0'
        response["selectproject"] = project_name
    if select!=None:
        response["select"]=select
    else:
        select = '2'
        response["select"] = select
    if checkedenv_ids!=None:
        response["checkedenv_ids"] = checkedenv_ids
    else:
        response["checkedenv_ids"]=None
    return render(request, "./main/modules.html",response)
@login_required
def modules_add_data(request):
    Modules_name=request.POST.get("modules_name")
    Modules_desc=request.POST.get("modules_desc")
    developer = request.POST.get("developer")
    status = request.POST.get("status")
    project_name=request.POST.get('project_name')
    #得到外键数据
    project=Project.objects.get(project_name=project_name)
    code = len(Modules.objects.filter(Modules_name=Modules_name,Project=project).values())
    # 不重复则新增数据
    if code == 0:
        if status!=None:
            Modules.objects.create(Modules_name=Modules_name,Modules_desc=Modules_desc,Developer=developer,status=1,Project=project)
        else:
            Modules.objects.create(Modules_name=Modules_name, Modules_desc=Modules_desc,
                                   Developer=developer, status=0,Project=project)
        codeMessage = ""
    # 重复则不新增数据
    else:
        codeMessage = "同一个项目名下新增相同模块名，新增失败"
    # 根据用户过滤数据权限
    filiterdata = get_filiterdata(request)
    contacts = get_firstPagefiliterdata(Modules,filiterdata)

    # 获取测试人员名称
    testers_list = get_testers(Modules.objects.all().order_by("-id").filter(id__in=filiterdata))

    # 将模块数据和测试人员打包
    contactszip = zip(contacts, testers_list)

    project_names=get_project_name(filiterdata)
    return render(request, "./main/modules.html", {"modules": contactszip,"project_names":project_names,"code":code,"codeMessage":codeMessage,"modulees":contacts})

@login_required
def modules_edit_data(request):
    Modules_id = request.POST.get("id")
    Modules_name = request.POST.get("modules_name")
    Modules_desc = request.POST.get("modules_desc")
    developer = request.POST.get("developer")
    status = request.POST.get("status")
    project_name = request.POST.get('project_name')
    # 得到外键数据
    project = Project.objects.get(project_name=project_name)

    code = len(Modules.objects.filter(~Q(id=Modules_id), Modules_name=Modules_name,Project=project).values())
    # 不重复则更新数据
    if code == 0:
        if status != None:
            Modules.objects.filter(id=Modules_id).update(Modules_name=Modules_name, Modules_desc=Modules_desc, \
                                                          Developer=developer, status=1,
                                                         Project=project)
        else:
            Modules.objects.filter(id=Modules_id).update(Modules_name=Modules_name, Modules_desc=Modules_desc,
                                                         Developer=developer, status=0, Project=project)
        codeMessage = ""
    # 重复则不更新数据
    else:
        codeMessage = "同一个项目名下新增相同模块名，编辑失败"
    # 根据用户过滤数据权限
    filiterdata = get_filiterdata(request)
    contacts = get_firstPagefiliterdata(Modules, filiterdata)
    # 获取测试人员名称
    testers_list = get_testers(Modules.objects.all().order_by("-id").filter(id__in=filiterdata))

    # 将模块数据和测试人员打包
    contactszip = zip(contacts, testers_list)
    project_names = get_project_name(filiterdata)
    return render(request, "./main/modules.html", {"modules": contactszip, "project_names": project_names,"code":code,"codeMessage":codeMessage,"modulees":contacts})

@login_required
def modules_delete_data(request):
    modules_ids = request.POST.get("id")
    modules_ids=modules_ids.split(',')
    # 第一个传过来的值为None字符串 不需要
    modules_ids = modules_ids[1:]

    # 批量删除
    idstring = ','.join(modules_ids)
    Modules.objects.extra(where=['id IN (' + idstring + ')']).delete()

    # 根据用户过滤数据权限
    filiterdata = get_filiterdata(request)
    contacts = get_firstPagefiliterdata(Modules, filiterdata)
    # 获取测试人员名称
    testers_list = get_testers(Modules.objects.all().order_by("-id").filter(id__in=filiterdata))

    # 将模块数据和测试人员打包
    contactszip = zip(contacts, testers_list)
    project_names = get_project_name(filiterdata)
    return render(request, "./main/modules.html", {"modules": contactszip, "project_names": project_names,"modulees":contacts})

@login_required
def modules_search_name(request):
    modules_name = request.GET.get("modules_name")
    Developer = request.GET.get("Developer")
    select = request.GET.get("select")
    project_name=request.GET.get("project_name")
    if project_name=="0":
        if select != '2':
            modules_list = Modules.objects.filter(Q(Modules_name__contains=modules_name),
                                                  Q(Developer__contains=Developer), Q(status=select)).order_by("-id")
        else:
            modules_list = Modules.objects.filter(Q(Modules_name__contains=modules_name),
                                                  Q(Developer__contains=Developer)).order_by("-id")
    else:
        # 得到外键数据
        project = Project.objects.get(project_name=project_name)
        if select!='2':
            modules_list = Modules.objects.filter(Q(Modules_name__contains=modules_name),
                                            Q(Developer__contains=Developer),Q(status=select),Q(Project=project)).order_by("-id")
        else:
            modules_list = Modules.objects.filter(Q(Modules_name__contains=modules_name),
                                              Q(Developer__contains=Developer),Q(Project=project)).order_by("-id")

    # 根据用户过滤数据权限
    filiterdata = get_filiterdata(request)
    modules_list = modules_list.filter(id__in=filiterdata)

    # 获取测试人员名称
    testers_list = get_testers(modules_list)

    paginator = Paginator(modules_list, NumberColumns)
    contacts = paginator.page(1)

    # 将模块数据和测试人员打包
    contactszip = zip(contacts, testers_list)

    project_names = get_project_name(filiterdata)
    return render(request, "./main/modules.html", {"modules": contactszip,"modules_name":modules_name,"selectproject":project_name,\
                                                   "Developer":Developer,"select":select,"project_names": project_names,"modulees":contacts})

#测试用例
#当数据是部分时把列表的项目名取出
def filter_project_listnames(case_list):
    modules = case_list.values('Modules')
    project_listnames = []
    for i in modules:
        projects_id = Modules.objects.filter(id=i['Modules']).values("Project")
        project_name = Project.objects.filter(id=projects_id[0]['Project']).values("project_name")
        project_listnames.append(project_name[0]['project_name'])
    return project_listnames
#把测试模块的modules_name取出，当成新增编辑页面项目的可选的列
def get_modules_name(project_name,filiterdata):
    filiterdata_id_list=[]
    for filiter in filiterdata:
        filiterdata_id_list.append(filiter.id)
    # 得到外键数据
    project = Project.objects.get(project_name=project_name)
    modules_names = []
    startmodules_names = Modules.objects.filter(Project=project,status=1,id__in=filiterdata_id_list).values("Modules_name").order_by("-id")
    for i in range(len(startmodules_names)):
        modules_names.append(startmodules_names[i]['Modules_name'])
    return modules_names
#选择项目后出现对应的模块
'''
@login_required
def get_modules(request):
    project_name=request.GET.get("project_name")
    return JsonResponse{}
'''
#根据登录用户获取模块数据
def get_filiterdata(request):
    # 获取当前登录用户登录名
    current_user_set = str(request.user)
    user_queryset=User.objects.filter(username=current_user_set)
    for user in user_queryset:
        return user.modules_set.all()
@login_required
def case(request):
    case_name=request.GET.get("case_name")
    selectproject = request.GET.get("project_name")
    selectmodules = request.GET.get("modules_name")
    api = request.GET.get("api")
    version = request.GET.get("version")
    select = request.GET.get("select")
    checkedenv_ids=request.GET.get("checkedenv_ids")
    try:
        if selectproject == "0":
            if select != '2':
                case_list = Case.objects.filter(Q(case_name__contains=case_name), Q(api__contains=api),
                                                Q(version__contains=version), Q(status=select)).order_by("-id")
            else:
                case_list = Case.objects.filter(Q(case_name__contains=case_name), Q(api__contains=api),
                                                Q(version__contains=version)).order_by("-id")
        else:
            if selectmodules == "0":
                # 得到外键数据
                project = Project.objects.get(project_name=selectproject)
                # 得到用例的外键数据
                modules = Modules.objects.filter(Project=project)

                if select != '2':
                    case_list = Case.objects.filter(Q(case_name__contains=case_name), Q(api__contains=api),
                                                    Q(version__contains=version), Q(status=select),
                                                    Q(Modules__in=modules)).order_by("-id")
                else:
                    case_list = Case.objects.filter(Q(case_name__contains=case_name), Q(api__contains=api),
                                                    Q(version__contains=version), Q(Modules__in=modules)).order_by("-id")
            else:
                # 得到外键数据
                project = Project.objects.get(project_name=selectproject)
                # 得到用例的外键数据
                modules = Modules.objects.get(Modules_name=selectmodules, Project=project)
                if select != '2':
                    case_list = Case.objects.filter(Q(case_name__contains=case_name), Q(api__contains=api),
                                                    Q(version__contains=version), Q(status=select), Q(Modules=modules)).order_by("-id")
                else:
                    case_list = Case.objects.filter(Q(case_name__contains=case_name), Q(api__contains=api),
                                                    Q(version__contains=version), Q(Modules=modules)).order_by("-id")
    except:
        case_list=Case.objects.all().order_by("-id")

    #根据用户过滤数据权限
    filiterdata = get_filiterdata(request)
    case_list=case_list.filter(Modules__in=filiterdata)

    paginator=Paginator(case_list,NumberColumns)

    page=request.GET.get("page")
    try:
        contacts=paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts=paginator.page(paginator.num_pages)
    #得到列表项目名根据页面去提取
    project_listnames=filter_project_listnames(case_list)

    newproject_listnames=[]
    try:
        first_number=NumberColumns*int(page)-NumberColumns
        last_number=NumberColumns*int(page)
        #print (first_number)
        #print (last_number)
        if last_number>len(project_listnames):
            last_number=len(project_listnames)
        for i in range(first_number,last_number):
            newproject_listnames.append(project_listnames[i])
    except:
        newproject_listnames=project_listnames


    project_names=get_project_name(filiterdata)
    #修复没有数据索引越界的问题
    try:
        project_name=project_names[0]
        modules_names = get_modules_name(project_name,filiterdata)
    except:
        project_name=None
        modules_names=None
    #把项目名和用例列表数据打包
    contactszip=zip(contacts,newproject_listnames)
    #给项目选择框对应的数据
    if selectproject!="0" and selectproject!=None :
        selectmodules_names=get_modules_name(selectproject,filiterdata)
    else:
        selectmodules_names=None

    response={"casees":contacts,"cases":contactszip,"selectmodules_names":selectmodules_names}
    if case_name!=None:
        response["case_name"]=case_name
    if api!=None:
        response["api"]=api
    if version!=None:
        response["version"]=version
    if project_names!=None:
        response["project_names"]=project_names
    if modules_names!=None:
        response["modules_names"]=modules_names
    if selectproject!=None:
        response["selectproject"]=selectproject
    else:
        selectproject = '0'
        response["selectproject"] = selectproject
    if selectmodules!=None:
        response["selectmodules"]=selectmodules
    else:
        selectmodules = '0'
        response["selectmodules"] = selectmodules
    if select!=None:
        response["select"]=select
    else:
        select = '2'
        response["select"] = select
    #print(checkedenv_ids)
    if checkedenv_ids!=None:
        #checkedenv_ids = checkedenv_ids.split(',')
        #print(checkedenv_ids)
        response["checkedenv_ids"] = checkedenv_ids
    else:
        response["checkedenv_ids"]=None
    return render(request, "./main/case.html",response)
#通过项目名去获取模块名并返回
@login_required
def get_modules(request):
    project_name=request.GET.get("project_name")
    # 根据用户过滤数据权限
    filiterdata = get_filiterdata(request)
    modules_names=get_modules_name(project_name,filiterdata)
    return JsonResponse({"modules_names":modules_names})

@login_required
def case_add_data(request):
    case_name=request.POST.get("case_name")
    project_name=request.POST.get("project_name")
    modules_name = request.POST.get("modules_name")
    api = request.POST.get("api")
    version = request.POST.get("version")
    case_desc=request.POST.get('case_desc')
    status = request.POST.get('status')
    #得到项目的外键数据
    project=Project.objects.get(project_name=project_name)
    #得到用例的外键数据
    modules=Modules.objects.get(Modules_name=modules_name,Project=project)

    try:
        int(case_name)
        code = -1  # 名字不允许全部为数字
        codeMessage = "接口名不允许全部为数字，新增失败"

    except:
        code = len(Case.objects.filter(case_name=case_name).values())
        # 不重复则新增数据
        if code == 0:
            if status!=None:
                Case.objects.create(case_name=case_name,case_desc=case_desc,api=api,version=version,status=1,Modules=modules)
            else:
                Case.objects.create(case_name=case_name,case_desc=case_desc,api=api,version=version,status=0,Modules=modules)
            codeMessage = ""
        # 重复则不新增数据
        else:
            codeMessage = "接口名称重复，新增失败"

    # 根据用户过滤数据权限
    filiterdata = get_filiterdata(request)
    Case_list = Case.objects.all().order_by("-id")
    Case_list = Case_list.filter(Modules__in=filiterdata)
    paginator = Paginator(Case_list, NumberColumns)
    contacts = paginator.page(1)

    # 得到列表项目名
    project_listnames = filter_project_listnames(Case_list)
    # 把项目名和用例列表数据打包
    contactszip = zip(contacts, project_listnames)
    project_names=get_project_name(filiterdata)
    project_name = project_names[0]
    modules_names = get_modules_name(project_name,filiterdata)
    return render(request, "./main/case.html", {"cases": contactszip,"modules_names": modules_names, "project_names": project_names,"casees":contacts,"code":code,"codeMessage":codeMessage})

@login_required
def case_edit_data(request):
    case_id = request.POST.get("id")
    case_name = request.POST.get("case_name")
    project_name = request.POST.get("project_name")
    modules_name = request.POST.get("modules_name")
    api = request.POST.get("api")
    version = request.POST.get("version")
    case_desc = request.POST.get('case_desc')
    status = request.POST.get('status')
    # 得到项目的外键数据
    project = Project.objects.get(project_name=project_name)
    # 得到用例的外键数据
    modules = Modules.objects.get(Modules_name=modules_name, Project=project)

    try:
        int(case_name)
        code = -1  # 名字不允许全部为数字
        codeMessage = "接口名不允许全部为数字，编辑失败"

    except:
        code = len(Case.objects.filter(~Q(id=case_id), case_name=case_name).values())
        # 不重复则更新数据
        if code == 0:
            if status != None:
                Case.objects.filter(id=case_id).update(case_name=case_name, case_desc=case_desc, api=api, version=version,
                                                       status=1, Modules=modules)
            else:
                Case.objects.filter(id=case_id).update(case_name=case_name, case_desc=case_desc, api=api, version=version,
                                                       status=0, Modules=modules)
            codeMessage = ""
        # 重复则不更新数据
        else:
            codeMessage = "接口名称重复，修改失败"
    # 根据用户过滤数据权限
    filiterdata = get_filiterdata(request)
    Case_list = Case.objects.all().order_by("-id")
    Case_list = Case_list.filter(Modules__in=filiterdata)
    paginator = Paginator(Case_list, NumberColumns)
    contacts = paginator.page(1)

    # 得到列表项目名
    project_listnames = filter_project_listnames(Case_list)
    #把项目名和用例列表数据打包
    contactszip = zip(contacts, project_listnames)
    project_names = get_project_name(filiterdata)
    project_name = project_names[0]
    modules_names = get_modules_name(project_name,filiterdata)
    return render(request, "./main/case.html",
                  {"cases": contactszip, "modules_names": modules_names, "project_names": project_names,"casees":contacts,"code":code,"codeMessage":codeMessage})

@login_required
def case_delete_data(request):
    case_ids = request.POST.get("id")
    case_ids=case_ids.split(',')
    # 第一个传过来的值为None字符串 不需要
    case_ids = case_ids[1:]

    # 批量删除
    idstring = ','.join(case_ids)
    Case.objects.extra(where=['id IN (' + idstring + ')']).delete()

    # 根据用户过滤数据权限
    filiterdata = get_filiterdata(request)
    Case_list = Case.objects.all().order_by("-id")
    Case_list = Case_list.filter(Modules__in=filiterdata)
    paginator = Paginator(Case_list, NumberColumns)
    contacts = paginator.page(1)

    # 得到列表项目名
    project_listnames = filter_project_listnames(Case_list)
    #把项目名和用例列表数据打包
    contactszip = zip(contacts, project_listnames)
    project_names = get_project_name(filiterdata)
    project_name = project_names[0]
    modules_names = get_modules_name(project_name,filiterdata)
    return render(request, "./main/case.html",
                  {"cases": contactszip, "modules_names": modules_names, "project_names": project_names,"casees":contacts})

@login_required
def case_search_name(request):
    case_name = request.GET.get("case_name")
    api = request.GET.get("api")
    version = request.GET.get("version")
    select = request.GET.get("select")
    selectproject=request.GET.get("project_name")
    selectmodules = request.GET.get("modules_name")
    if selectproject=="0":
        if select != '2':
            case_list = Case.objects.filter(Q(case_name__contains=case_name), Q(api__contains=api),
                                                  Q(version__contains=version), Q(status=select)).order_by("-id")
        else:
            case_list = Case.objects.filter(Q(case_name__contains=case_name), Q(api__contains=api),
                                                  Q(version__contains=version)).order_by("-id")
    else:
        if selectmodules=="0":
            # 得到外键数据
            project = Project.objects.get(project_name=selectproject)
            # 得到用例的外键数据
            modules = Modules.objects.filter(Project=project)
            if select!='2':
                case_list = Case.objects.filter(Q(case_name__contains=case_name), Q(api__contains=api),
                                                  Q(version__contains=version), Q(status=select),Q(Modules__in=modules)).order_by("-id")
            else:
                case_list = Case.objects.filter(Q(case_name__contains=case_name), Q(api__contains=api),
                                                  Q(version__contains=version),Q(Modules__in=modules)).order_by("-id")
        else:
            # 得到外键数据
            project = Project.objects.get(project_name=selectproject)
            # 得到用例的外键数据
            modules = Modules.objects.get(Modules_name=selectmodules, Project=project)
            if select!='2':
                case_list = Case.objects.filter(Q(case_name__contains=case_name), Q(api__contains=api),
                                                  Q(version__contains=version), Q(status=select),Q(Modules=modules)).order_by("-id")
            else:
                case_list = Case.objects.filter(Q(case_name__contains=case_name), Q(api__contains=api),
                                                  Q(version__contains=version), Q(Modules=modules)).order_by("-id")
    # 根据用户过滤数据权限
    filiterdata = get_filiterdata(request)
    case_list = case_list.filter(Modules__in=filiterdata)

    paginator = Paginator(case_list, NumberColumns)
    contacts = paginator.page(1)
    # 得到列表项目名
    project_listnames = filter_project_listnames(case_list)
    # 把项目名和用例列表数据打包
    contactszip = zip(contacts, project_listnames)
    project_names = get_project_name(filiterdata)
    if project_names:
        project_name = project_names[0]
        modules_names = get_modules_name(project_name,filiterdata)
    else:
        modules_names=[]
    #给项目选择框对应的数据
    if selectproject!="0":
        selectmodules_names=get_modules_name(selectproject,filiterdata)
    else:
        selectmodules_names=None
    return render(request, "./main/case.html", {"cases": contactszip, "modules_names": modules_names, "project_names": project_names,\
                                                "case_name":case_name,"api":api,"version":version,"select":select,\
                                                "selectmodules_names":selectmodules_names,"selectproject":selectproject,"selectmodules":selectmodules,"casees":contacts})

#测试步骤

#把测试用例的project_name取出，当成新增编辑页面项目的可选的列
def get_case_name(Case_dataqueryset):
    case_names = []
    case_namelist = Case.objects.filter(status=1,id__in=Case_dataqueryset).values('case_name').order_by("-id")
    for i in range(len(case_namelist)):
        case_names.append(case_namelist[i]['case_name'])
    return case_names

#根据登录用户获取case的数据
def get_filiterCasedata(request):
    return Case.objects.filter(Modules__in=get_filiterdata(request))

def step(request):
    step_name = request.GET.get("step_name")
    method = request.GET.get("method")
    steplevel = request.GET.get("steplevel")
    select = request.GET.get("select")
    case_name = request.GET.get("case_name")
    checkedenv_ids = request.GET.get("checkedenv_ids")
    try:
        if case_name == "0":
            if method == "0":
                if select == '2':
                    step_list = Step.objects.filter(Q(step_name__contains=step_name), Q(steplevel__contains=steplevel)).order_by("-id")
                else:
                    step_list = Step.objects.filter(Q(step_name__contains=step_name), Q(steplevel__contains=steplevel), \
                                                    Q(status=select)).order_by("-id")
            else:
                if select == '2':
                    step_list = Step.objects.filter(Q(step_name__contains=step_name), Q(steplevel__contains=steplevel), \
                                                    Q(method=method)).order_by("-id")
                else:
                    step_list = Step.objects.filter(Q(step_name__contains=step_name), Q(steplevel__contains=steplevel), \
                                                    Q(status=select), Q(method=method)).order_by("-id")
        else:
            # 得到外键数据
            case = Case.objects.get(case_name=case_name)
            if method == "0":
                if select == '2':
                    step_list = Step.objects.filter(Q(step_name__contains=step_name), Q(steplevel__contains=steplevel), \
                                                    Q(case=case)).order_by("-id")
                else:
                    step_list = Step.objects.filter(Q(step_name__contains=step_name), Q(steplevel__contains=steplevel), \
                                                    Q(status=select), Q(case=case)).order_by("-id")
            else:
                if select == '2':
                    step_list = Step.objects.filter(Q(step_name__contains=step_name), Q(steplevel__contains=steplevel), \
                                                    Q(method=method), Q(case=case)).order_by("-id")
                else:
                    step_list = Step.objects.filter(Q(step_name__contains=step_name), Q(steplevel__contains=steplevel), \
                                                    Q(status=select), Q(method=method), Q(case=case)).order_by("-id")
    except:
        step_list=Step.objects.all().order_by("-id")
    # 根据登录用户获取相关数据
    Case_dataqueryset = get_filiterCasedata(request)
    step_list=step_list.filter(case__in=Case_dataqueryset)

    paginator=Paginator(step_list,NumberColumns)
    page=request.GET.get("page")
    try:
        contacts=paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts=paginator.page(paginator.num_pages)
    response={"steps":contacts}
    # 新增和编辑时的用例名
    case_names = get_case_name(Case_dataqueryset)
    # 根据登录用户获取相关数据
    Step_dataqueryset = get_filiterStepdata(request)
    step_names=get_step_name(Step_dataqueryset)

    if step_name!=None:
        response["step_name"]=step_name
    if steplevel!=None:
        response["steplevel"]=steplevel
    if case_names!=None:
        response["case_names"]=case_names
    if step_names!=None:
        response["step_names"]=step_names
    if case_name!=None:
        response["selectcase_name"]=case_name
    else:
        case_name = '0'
        response["selectcase_name"] = case_name
    if method!=None:
        response["selectmethod"]=method
    else:
        method = '0'
        response["selectmethod"] = method
    if select!=None:
        response["select"]=select
    else:
        select = '2'
        response["select"] = select
    if checkedenv_ids!=None:
        response["checkedenv_ids"] = checkedenv_ids
    else:
        response["checkedenv_ids"]=None
    return render(request, "./main/step.html",response)


#获取权重
def get_weights(step_name,api_dependency):
    oldstep_weights=0
    api_dependencyjson = json.loads(api_dependency)
    for variable in api_dependencyjson.keys():
        for reference_step_name in api_dependencyjson[variable].keys():
            oldreference_step_weights = Step.objects.filter(step_name=reference_step_name).values('step_weights')[0]['step_weights']
            if oldreference_step_weights+1>oldstep_weights:
                Step.objects.filter(step_name=step_name).update(step_weights=oldreference_step_weights+1)
                oldstep_weights=oldreference_step_weights+1

#获取权重
def get_case_weights(step_name,api_dependency):
    oldcase_weights=0
    case_id = Step.objects.filter(step_name=step_name).values('case_id')[0]['case_id']
    step_names=Step.objects.filter(case=case_id).values('step_name')
    #用例下所有步骤
    for case_step_name in step_names:
        reference_step_names=Reference_step.objects.filter(step_name=case_step_name['step_name']).values('reference_step_name')
        oldstep_weights = 0
        for reference_step_name in reference_step_names:
            reference_case_id=Step.objects.filter(step_name=reference_step_name['reference_step_name']).values('case_id')[0]['case_id']
            reference_case_step_names=Step.objects.filter(case=reference_case_id).values('step_name')
            #被依赖下的用例下的所有步骤
            for reference_case_step_name in reference_case_step_names:
                old_case_step_weights = \
                Step.objects.filter(step_name=reference_case_step_name['step_name']).values('step_weights')[0]['step_weights']
                if old_case_step_weights + 1 > oldstep_weights:
                    oldstep_weights = old_case_step_weights + 1
        if oldstep_weights>oldcase_weights:
            oldcase_weights=oldstep_weights
    Case.objects.filter(id=case_id).update(case_weights=oldcase_weights)

#当中间步骤树节点变化时 向上遍历直到结尾
def change_step_case(step_name):
    #先修改涉及到的步骤权重
    Dependent_step_cases=Reference_step.objects.filter(reference_step_name=step_name).values('step_name')
    count=0
    while len(Dependent_step_cases)!=count:
        count=0
        Dependent_steps = []
        for Dependent_step_case in Dependent_step_cases:
            api_dependency=Step.objects.filter(step_name=Dependent_step_case['step_name']).values('api_dependency')[0]['api_dependency']
            get_weights(Dependent_step_case['step_name'], api_dependency)
            Dependent_steps.append(Dependent_step_case['step_name'])
        for Dependent_step_case in Dependent_steps:
            Dependent_step_cases = Reference_step.objects.filter(reference_step_name=Dependent_step_case).values('step_name')
            if len(Dependent_step_cases)==0:
                count+=1
        else:
            Dependent_steps=[]
    #再修改用例权重
    Dependent_step_cases = Reference_step.objects.filter(reference_step_name=step_name).values('step_name')
    count = 0
    while len(Dependent_step_cases) != count:
        count = 0
        Dependent_steps = []
        for Dependent_step_case in Dependent_step_cases:
            api_dependency = \
            Step.objects.filter(step_name=Dependent_step_case['step_name']).values('api_dependency')[0][
                'api_dependency']
            get_case_weights(Dependent_step_case['step_name'], api_dependency)
            Dependent_steps.append(Dependent_step_case['step_name'])
        for Dependent_step_case in Dependent_steps:
            Dependent_step_cases = Reference_step.objects.filter(reference_step_name=Dependent_step_case).values(
                'step_name')
            if len(Dependent_step_cases) == 0:
                count += 1
        else:
            Dependent_steps = []



@login_required
def step_add_data(request):
    step_name=request.POST.get('step_name')
    case_name=request.POST.get('case_name')
    method = request.POST.get('method')
    headers = request.POST.get('headers')
    params = request.POST.get('params')
    asserts = request.POST.get('asserts')
    api_dependency=request.POST.get('ApiDependencys')
    steplevel = request.POST.get('steplevel')
    step_desc = request.POST.get('step_desc')
    status = request.POST.get('status')
    paramsbody = request.POST.get('paramsbody')
    # 得到外键数据
    case = Case.objects.get(case_name=case_name)
    if asserts == None:
        asserts=""
    if api_dependency == None:
        api_dependency=""
    try:
        int(step_name)
        code = -1  # 名字不允许全部为数字
        codeMessage = "用例名不允许全部为数字，新增失败"

    except:
        code = len(Step.objects.filter(step_name=step_name).values())

        # 不重复则新增数据
        if code == 0:
            if method == "get" or method == "postform":
                if status != None:
                    Step.objects.create(step_name=step_name, step_desc=step_desc, steplevel=steplevel, method=method, \
                                        headers=headers, params=params, assert_response=asserts,
                                        api_dependency=api_dependency, status=1, case=case)
                else:
                    Step.objects.create(step_name=step_name, step_desc=step_desc, steplevel=steplevel, method=method, \
                                        headers=headers, params=params, assert_response=asserts,
                                        api_dependency=api_dependency, status=0, case=case)
            elif method == "postbody" or method == "put" or method == "delete":
                if status != None:
                    Step.objects.create(step_name=step_name, step_desc=step_desc, steplevel=steplevel, method=method, \
                                        headers=headers, params=paramsbody, assert_response=asserts,
                                        api_dependency=api_dependency, status=1, case=case)
                else:
                    Step.objects.create(step_name=step_name, step_desc=step_desc, steplevel=steplevel, method=method, \
                                        headers=headers, params=paramsbody, assert_response=asserts,
                                        api_dependency=api_dependency, status=0, case=case)
            if api_dependency != "":
                # 得到外键数据
                step = Step.objects.get(step_name=step_name)
                # 插入接口依赖数据
                api_dependencyjson = json.loads(api_dependency)
                for variable in api_dependencyjson.keys():
                    for reference_step_name in api_dependencyjson[variable].keys():
                        Reference_step.objects.create(variable=variable, step_name=step_name,
                                                      path=api_dependencyjson[variable][reference_step_name],
                                                      reference_step_name=reference_step_name, step=step)
                # 获取权重
                get_weights(step_name, api_dependency)
            else:
                Step.objects.filter(step_name=step_name).update(step_weights=0)
            # 获得权重
            get_case_weights(step_name, api_dependency)
            change_step_case(step_name)
            codeMessage = ""
            # 更新用例的stepCount
            db.updateStepCount(step_name)
        # 重复则不新增数据
        else:
            codeMessage = "用例名重复，新增失败"

    #用作接口依赖选择框
    Step_dataqueryset = get_filiterStepdata(request)
    step_names = get_step_name(Step_dataqueryset)
    #新增和编辑时的用例名
    # 根据登录用户获取相关数据
    Case_dataqueryset = get_filiterCasedata(request)
    contacts = get_firstPagefiliterdata(Step, Case_dataqueryset)
    case_names = get_case_name(Case_dataqueryset)
    return render(request, "./main/step.html", {"steps": contacts,"case_names": case_names,"code":code,"codeMessage":codeMessage,"step_names":step_names})

@login_required
def step_edit_data(request):
    step_id = request.POST.get("id")
    step_name = request.POST.get('step_name')
    case_name = request.POST.get('case_name')
    method = request.POST.get('method')
    headers = request.POST.get('headers')
    params = request.POST.get('params')
    asserts = request.POST.get('asserts')
    api_dependency = request.POST.get('ApiDependencys')
    steplevel = request.POST.get('steplevel')
    step_desc = request.POST.get('step_desc')
    status = request.POST.get('status')
    paramsbody = request.POST.get('paramsbody')

    # 得到外键数据
    case = Case.objects.get(case_name=case_name)

    try:
        int(step_name)
        code = -1  # 名字不允许全部为数字
        codeMessage = "用例名不允许全部为数字，编辑失败"
    except:
        code = len(Step.objects.filter(~Q(id=step_id), step_name=step_name).values())
        # 不重复则更新数据
        if code == 0:
            if asserts == None:
                asserts = ""
            if api_dependency == None:
                api_dependency = ""

            oldapi_dependencys = Step.objects.filter(step_name=step_name).values('api_dependency')

            if method == "get" or method == "postform":
                if status != None:
                    Step.objects.filter(id=step_id).update(step_name=step_name, step_desc=step_desc, steplevel=steplevel,
                                                           method=method, \
                                                           headers=headers, params=params, assert_response=asserts,
                                                           api_dependency=api_dependency, status=1, case=case)
                else:
                    Step.objects.filter(id=step_id).update(step_name=step_name, step_desc=step_desc, steplevel=steplevel,
                                                           method=method, \
                                                           headers=headers, params=params, assert_response=asserts,
                                                           api_dependency=api_dependency, status=0, case=case)
            elif method == "postbody" or method == "put" or method == "delete":
                if status != None:
                    Step.objects.filter(id=step_id).update(step_name=step_name, step_desc=step_desc, steplevel=steplevel,
                                                           method=method, \
                                                           headers=headers, params=paramsbody, assert_response=asserts,
                                                           api_dependency=api_dependency, status=1, case=case)
                else:
                    Step.objects.filter(id=step_id).update(step_name=step_name, step_desc=step_desc, steplevel=steplevel,
                                                           method=method, \
                                                           headers=headers, params=paramsbody, assert_response=asserts,
                                                           api_dependency=api_dependency, status=0, case=case)
            # 得到外键数据
            step = Step.objects.get(step_name=step_name)

            if api_dependency != "":
                # 先删除接口依赖的数据
                Reference_step.objects.filter(step=step).delete()
                # 插入接口依赖数据
                api_dependencyjson = json.loads(api_dependency)
                for variable in api_dependencyjson.keys():
                    for reference_step_name in api_dependencyjson[variable].keys():
                        Reference_step.objects.create(variable=variable, step_name=step_name,
                                                      path=api_dependencyjson[variable][reference_step_name],
                                                      reference_step_name=reference_step_name, step=step)

                # 获取权重
                get_weights(step_name, api_dependency)
            else:
                # 先删除接口依赖的数据
                Reference_step.objects.filter(step=step).delete()
                # 写入权重
                Step.objects.filter(step_name=step_name).update(step_weights=0)
            # 获得权重
            get_case_weights(step_name, api_dependency)
            change_step_case(step_name)
            codeMessage = ""

            #更新用例的stepCount
            db.updateStepCount(step_name)
        # 重复则不更新数据
        else:
            codeMessage = "用例名重复，修改失败"

    # 用作接口依赖选择框
    Step_dataqueryset = get_filiterStepdata(request)
    step_names = get_step_name(Step_dataqueryset)
    # 新增和编辑时的用例名
    # 根据登录用户获取相关数据
    Case_dataqueryset = get_filiterCasedata(request)
    contacts = get_firstPagefiliterdata(Step, Case_dataqueryset)

    case_names = get_case_name(Case_dataqueryset)
    return render(request, "./main/step.html", {"steps": contacts, "case_names": case_names,"step_names":step_names,"code":code,"codeMessage":codeMessage})
#获取表的列名
def get_columu(modelstr):
    modelobj = apps.get_model("request", modelstr)
    fields = []
    for field in modelobj._meta.fields:
        field = field.verbose_name.replace(' ', '_')
        fields.append(field)
    return fields
#复制的数据处理
def set_data(modelstr,model,copystep,step):
    fields = get_columu(modelstr)
    dataslist = model.objects.filter(step=copystep).values_list()
    for tupledata in dataslist:
        listdata = list(tupledata)
        listdata[1] = step
        #print (dict(zip(fields[1:],listdata[1:])))
        model.objects.create(**dict(zip(fields[1:],listdata[1:])))
@login_required
def step_copy_data(request):
    step_name=request.POST.get('step_name')
    copystep_name=request.POST.get('copystep_name')

    try:
        int(step_name)
        code = -1  # 名字不允许全部为数字
        codeMessage = "用例名不允许全部为数字，复制失败"

    except:
        code = len(Step.objects.filter(step_name=step_name).values())

        # 不重复则新增数据
        if code == 0:
            # 得到复制源数据外键
            copystep = Step.objects.get(step_name=copystep_name)

            fields=get_columu("Step")
            #插入step表的数据
            dataslist=Step.objects.filter(step_name=copystep_name).values_list()
            for tupledata in dataslist:
                listdata=list(tupledata)
                listdata[2]=step_name
                # 得到外键数据
                listdata[1] = Case.objects.get(id=listdata[1])
                Step.objects.create(**dict(zip(fields[1:],listdata[1:])))
            # 得到将要新建数据的外键
            step = Step.objects.get(step_name=step_name)
            #插入sql表的数据
            set_data("Sql",Sql, copystep,step)
            #插入nosql表的数据
            set_data("NoSql",NoSql,copystep, step)
            #插入Reference_step表的数据
            set_data("Reference_step",Reference_step,copystep, step)
            codeMessage = ""
            # 更新用例的stepCount
            db.updateStepCount(step_name)
        # 重复则不新增数据
        else:
            codeMessage = "用例名重复，复制失败"

    #用作接口依赖选择框
    Step_dataqueryset = get_filiterStepdata(request)
    step_names = get_step_name(Step_dataqueryset)
    #新增和编辑时的用例名
    # 根据登录用户获取相关数据
    Case_dataqueryset = get_filiterCasedata(request)
    contacts = get_firstPagefiliterdata(Step, Case_dataqueryset)
    case_names = get_case_name(Case_dataqueryset)
    return render(request, "./main/step.html", {"steps": contacts,"case_names": case_names,"code":code,"codeMessage":codeMessage,"step_names":step_names})

@login_required
def step_delete_data(request):
    step_ids = request.POST.get("id")
    step_ids=step_ids.split(',')
    # 第一个传过来的值为None字符串 不需要
    step_ids = step_ids[1:]

    # 批量删除
    idstring = ','.join(step_ids)

    # 更新用例的stepCount
    db.updateDeleteStepCount(idstring)
    Step.objects.extra(where=['id IN (' + idstring + ')']).delete()

    # 用作接口依赖选择框
    Step_dataqueryset = get_filiterStepdata(request)
    step_names = get_step_name(Step_dataqueryset)
    # 新增和编辑时的用例名
    # 根据登录用户获取相关数据
    Case_dataqueryset = get_filiterCasedata(request)
    contacts = get_firstPagefiliterdata(Step, Case_dataqueryset)

    case_names = get_case_name(Case_dataqueryset)
    return render(request, "./main/step.html", {"steps": contacts, "case_names": case_names,"step_names":step_names})

@login_required
def step_search_name(request):
    step_name = request.GET.get("step_name")
    method = request.GET.get("method")
    steplevel = request.GET.get("steplevel")
    select = request.GET.get("select")
    case_name=request.GET.get("case_name")
    print (1)
    if case_name=="0":
        if method=="0":
            if select == '2':
                step_list = Step.objects.filter(Q(step_name__contains=step_name), Q(steplevel__contains=steplevel)).order_by("-id")
            else:
                step_list = Step.objects.filter(Q(step_name__contains=step_name), Q(steplevel__contains=steplevel),\
                                                  Q(status=select)).order_by("-id")
        else:
            if select == '2':
                step_list = Step.objects.filter(Q(step_name__contains=step_name), Q(steplevel__contains=steplevel), \
                                                    Q(method=method)).order_by("-id")
            else:
                step_list = Step.objects.filter(Q(step_name__contains=step_name), Q(steplevel__contains=steplevel),\
                                                  Q(status=select),Q(method=method)).order_by("-id")
    else:
        # 得到外键数据
        case = Case.objects.get(case_name=case_name)
        if method=="0":
            if select == '2':
                step_list = Step.objects.filter(Q(step_name__contains=step_name), Q(steplevel__contains=steplevel),\
                                                Q(case=case)).order_by("-id")
            else:
                step_list = Step.objects.filter(Q(step_name__contains=step_name), Q(steplevel__contains=steplevel),\
                                                  Q(status=select),Q(case=case)).order_by("-id")
        else:
            if select == '2':
                step_list = Step.objects.filter(Q(step_name__contains=step_name), Q(steplevel__contains=steplevel), \
                                                    Q(method=method),Q(case=case)).order_by("-id")
            else:
                step_list = Step.objects.filter(Q(step_name__contains=step_name), Q(steplevel__contains=steplevel),\
                                                  Q(status=select),Q(method=method),Q(case=case)).order_by("-id")
    # 根据登录用户获取相关数据
    Case_dataqueryset = get_filiterCasedata(request)
    step_list = step_list.filter(case__in=Case_dataqueryset)
    # 用作接口依赖选择框
    Step_dataqueryset = get_filiterStepdata(request)
    step_names = get_step_name(Step_dataqueryset)
    # 新增和编辑时的用例名
    paginator = Paginator(step_list, NumberColumns)
    contacts = paginator.page(1)
    case_names = get_case_name(Case_dataqueryset)
    return render(request, "./main/step.html", {"steps": contacts, "case_names": case_names,"select":select,"step_name":step_name,\
                                                "steplevel":steplevel,"selectcase_name":case_name,"selectmethod":method,"step_names":step_names})


#测试sql
#把测试步骤的step_name取出，当成新增编辑页面项目的可选的列
def get_step_name(Step_dataqueryset):
    step_names = []
    startstep_names = Step.objects.filter(status=1,id__in=Step_dataqueryset).values("step_name").order_by("-id")
    for i in range(len(startstep_names)):
        step_names.append(startstep_names[i]['step_name'])
    return step_names

#得到sql中db信息
def get_sqldb(request):
    # 需要添加数据库信息
    db_remarks = []
    try:
        datalist=Db.objects.values('db_remark')
        for data in datalist:
            db_remarks.append(data['db_remark'])
    except:
        pass
    return db_remarks

#根据登录用户获取case的数据
def get_filiterStepdata(request):
    return Step.objects.filter(case__in=get_filiterCasedata(request))


@login_required
def sql(request):
    #需要添加数据库信息
    db_remarks=get_sqldb(request)

    step_name = request.GET.get("step_name")
    selectdb_remark = request.GET.get("selectdb_remark")
    selectisselect = request.GET.get("selectisselect")
    select = request.GET.get("select")
    checkedenv_ids = request.GET.get("checkedenv_ids")
    try:
        if step_name == "0" and selectdb_remark == "0":
            if select != '2':
                if selectisselect != '2':
                    sql_list = Sql.objects.filter(Q(is_select=selectisselect), Q(status=select)).order_by("-id")
                else:
                    sql_list = Sql.objects.filter(Q(status=select)).order_by("-id")
            else:
                if selectisselect != '2':
                    sql_list = Sql.objects.filter(Q(is_select=selectisselect)).order_by("-id")
                else:
                    sql_list = Sql.objects.filter().order_by("-id")
        elif step_name == "0" and selectdb_remark != "0":
            if select != '2':
                if selectisselect != '2':
                    sql_list = Sql.objects.filter(Q(db_remark=selectdb_remark), Q(is_select=selectisselect),
                                                  Q(status=select)).order_by("-id")
                else:
                    sql_list = Sql.objects.filter(Q(db_remark=selectdb_remark), Q(status=select)).order_by("-id")
            else:
                if selectisselect != '2':
                    sql_list = Sql.objects.filter(Q(db_remark=selectdb_remark), Q(is_select=selectisselect)).order_by("-id")
                else:
                    sql_list = Sql.objects.filter(Q(db_remark=selectdb_remark)).order_by("-id")
        elif step_name != "0" and selectdb_remark != "0":
            # 得到外键数据
            step = Step.objects.get(step_name=step_name)
            if select != '2':
                if selectisselect != '2':
                    sql_list = Sql.objects.filter(Q(step=step), Q(db_remark=selectdb_remark), Q(is_select=selectisselect),
                                                  Q(status=select)).order_by(
                        "-id")
                else:
                    sql_list = Sql.objects.filter(Q(step=step), Q(db_remark=selectdb_remark), Q(status=select)).order_by(
                        "-id")
            else:
                if selectisselect != '2':
                    sql_list = Sql.objects.filter(Q(step=step), Q(db_remark=selectdb_remark),
                                                  Q(is_select=selectisselect)).order_by("-id")
                else:
                    sql_list = Sql.objects.filter(Q(step=step), Q(db_remark=selectdb_remark)).order_by("-id")
        else:
            # 得到外键数据
            step = Step.objects.get(step_name=step_name)
            if select != '2':
                if selectisselect != '2':
                    sql_list = Sql.objects.filter(Q(step=step), Q(is_select=selectisselect), Q(status=select)).order_by(
                        "-id")
                else:
                    sql_list = Sql.objects.filter(Q(step=step), Q(status=select)).order_by("-id")
            else:
                if selectisselect != '2':
                    sql_list = Sql.objects.filter(Q(step=step), Q(is_select=selectisselect)).order_by("-id")
                else:
                    sql_list = Sql.objects.filter(Q(step=step)).order_by("-id")
    except:
        sql_list=Sql.objects.all().order_by("-id")
    # 根据登录用户获取相关数据
    Step_dataqueryset = get_filiterStepdata(request)
    sql_list = sql_list.filter(step__in=Step_dataqueryset)

    paginator=Paginator(sql_list,NumberColumns)
    page=request.GET.get("page")
    try:
        contacts=paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts=paginator.page(paginator.num_pages)
    response={"sqls":contacts}
    step_names = get_step_name(Step_dataqueryset)

    if step_names!=None:
        response["step_names"]=step_names
    if step_name!=None:
        response["selectstep"]=step_name
    else:
        step_name = '0'
        response["selectstep"] = step_name
    if selectdb_remark!=None:
        response["selectdb_remark"]=selectdb_remark
    else:
        selectdb_remark = '0'
        response["selectdb_remark"] = selectdb_remark
    if selectisselect!=None:
        response["selectisselect"]=selectisselect
    else:
        selectisselect = '2'
        response["selectisselect"] = selectisselect
    if select!=None:
        response["select"]=select
    else:
        select = '2'
        response["select"] = select
    if db_remarks!=None:
        response["db_remarks"]=db_remarks
    if checkedenv_ids!=None:
        response["checkedenv_ids"] = checkedenv_ids
    else:
        response["checkedenv_ids"]=None
    return render(request, "./main/sql.html",response)

#将选择的db和db_remark
def get_db_id(request,database_desc):
    db=""
    try:
        db=Db.objects.filter(db_remark=database_desc).values("id")[0]['id']
    except:
        pass
    return db
@login_required
def sql_add_data(request):
    step_name=request.POST.get("step_name")
    isselect=request.POST.get("isselect")
    variable = request.POST.get("variable")
    sql = request.POST.get("sql")
    sql_condition = request.POST.get("sql_condition")
    remake=request.POST.get('remake')
    status = request.POST.get('status')
    database_desc = request.POST.get("database_desc")
    # 需要添加数据库信息
    db_remarks = get_sqldb(request)
    #将选择的db和db_remark
    db =get_db_id(request, database_desc)

    #得到外键数据
    step=Step.objects.get(step_name=step_name)
    if isselect==None:
        isselect=0
        variable=""
    else:
        isselect = 1
    if status!=None:
        Sql.objects.create(is_select=isselect,variable=variable,sql=sql,sql_condition=sql_condition,remake=remake,status=1,step=step,db_remark=database_desc,db=db)
    else:
        Sql.objects.create(is_select=isselect,variable=variable,sql=sql,sql_condition=sql_condition,remake=remake,status=0,step=step,db_remark=database_desc,db=db)
    # 根据登录用户获取相关数据
    Step_dataqueryset = get_filiterStepdata(request)
    contacts = get_firstPagefiliterdata(Sql, Step_dataqueryset)

    step_names = get_step_name(Step_dataqueryset)
    return render(request, "./main/sql.html", {"sqls":contacts,"step_names": step_names,"db_remarks":db_remarks})

@login_required
def sql_edit_data(request):
    sql_id = request.POST.get("id")
    step_name = request.POST.get("step_name")
    isselect = request.POST.get("isselect")
    variable = request.POST.get("variable")
    sql = request.POST.get("sql")
    sql_condition = request.POST.get("sql_condition")
    remake = request.POST.get('remake')
    status = request.POST.get('status')
    database_desc = request.POST.get("database_desc")

    # 需要添加数据库信息
    db_remarks = get_sqldb(request)
    # 将选择的db和db_remark
    db = get_db_id(request, database_desc)

    # 得到外键数据
    step = Step.objects.get(step_name=step_name)
    if isselect == None:
        isselect = 0
        variable = ""
    else:
        isselect = 1
    if status!=None:
        Sql.objects.filter(id=sql_id).update(is_select=isselect,variable=variable,sql=sql,sql_condition=sql_condition,remake=remake,status=1,step=step,db_remark=database_desc,db=db)
    else:
        Sql.objects.filter(id=sql_id).update(is_select=isselect,variable=variable,sql=sql,sql_condition=sql_condition,remake=remake,status=0,step=step,db_remark=database_desc,db=db)
    # 根据登录用户获取相关数据
    Step_dataqueryset = get_filiterStepdata(request)
    contacts = get_firstPagefiliterdata(Sql, Step_dataqueryset)

    step_names = get_step_name(Step_dataqueryset)
    return render(request, "./main/sql.html", {"sqls": contacts, "step_names": step_names,"db_remarks":db_remarks})

@login_required
def sql_delete_data(request):
    sql_ids = request.POST.get("id")
    # 需要添加数据库信息
    db_remarks = get_sqldb(request)

    sql_ids=sql_ids.split(',')
    # 第一个传过来的值为None字符串 不需要
    sql_ids = sql_ids[1:]

    # 批量删除
    idstring = ','.join(sql_ids)
    Sql.objects.extra(where=['id IN (' + idstring + ')']).delete()

    # 根据登录用户获取相关数据
    Step_dataqueryset = get_filiterStepdata(request)
    contacts = get_firstPagefiliterdata(Sql, Step_dataqueryset)

    step_names = get_step_name(Step_dataqueryset)
    return render(request, "./main/sql.html", {"sqls": contacts, "step_names": step_names,"db_remarks":db_remarks})

#批量修改appname
@login_required
def sql_editDb(request):
    sql_ids = request.POST.get("id")
    database_desc = request.POST.get("database_desc")
    # 需要添加数据库信息
    db_remarks = get_sqldb(request)
    # 将选择的db和db_remark
    db = get_db_id(request, database_desc)

    sql_ids=sql_ids.split(',')
    # 第一个传过来的值为None字符串 不需要
    sql_ids = sql_ids[1:]
    #数据库批量更新
    idstring = ','.join(sql_ids)
    Sql.objects.extra(where=['id IN (' + idstring + ')']).update(db_remark=database_desc,db=db)

    # 根据登录用户获取相关数据
    Step_dataqueryset = get_filiterStepdata(request)
    contacts = get_firstPagefiliterdata(Sql, Step_dataqueryset)

    step_names = get_step_name(Step_dataqueryset)
    return render(request, "./main/sql.html", {"sqls": contacts, "step_names": step_names,"db_remarks":db_remarks})

@login_required
def sql_search_name(request):
    step_name = request.GET.get("step_name")
    selectdb_remark = request.GET.get("selectdb_remark")
    selectisselect = request.GET.get("selectisselect")
    select = request.GET.get("select")

    # 需要添加数据库信息
    db_remarks = get_sqldb(request)

    if step_name=="0" and selectdb_remark=="0":
        if select != '2':
            if selectisselect!='2':
                sql_list = Sql.objects.filter(Q(is_select=selectisselect), Q(status=select)).order_by("-id")
            else:
                sql_list = Sql.objects.filter( Q(status=select)).order_by("-id")
        else:
            if selectisselect!='2':
                sql_list = Sql.objects.filter(Q(is_select=selectisselect)).order_by("-id")
            else:
                sql_list = Sql.objects.filter().order_by("-id")
    elif step_name=="0" and selectdb_remark!="0":
        if select != '2':
            if selectisselect!='2':
                sql_list = Sql.objects.filter(Q(db_remark=selectdb_remark), Q(is_select=selectisselect), Q(status=select)).order_by("-id")
            else:
                sql_list = Sql.objects.filter(Q(db_remark=selectdb_remark), Q(status=select)).order_by("-id")
        else:
            if selectisselect!='2':
                sql_list = Sql.objects.filter(Q(db_remark=selectdb_remark), Q(is_select=selectisselect)).order_by("-id")
            else:
                sql_list = Sql.objects.filter(Q(db_remark=selectdb_remark)).order_by("-id")
    elif step_name!="0" and selectdb_remark!="0":
        # 得到外键数据
        step = Step.objects.get(step_name=step_name)
        if select != '2':
            if selectisselect != '2':
                sql_list = Sql.objects.filter(Q(step=step), Q(db_remark=selectdb_remark), Q(is_select=selectisselect), Q(status=select)).order_by(
                    "-id")
            else:
                sql_list = Sql.objects.filter(Q(step=step), Q(db_remark=selectdb_remark), Q(status=select)).order_by("-id")
        else:
            if selectisselect != '2':
                sql_list = Sql.objects.filter(Q(step=step), Q(db_remark=selectdb_remark), Q(is_select=selectisselect)).order_by("-id")
            else:
                sql_list = Sql.objects.filter(Q(step=step), Q(db_remark=selectdb_remark)).order_by("-id")
    else:
        # 得到外键数据
        step = Step.objects.get(step_name=step_name)
        if select != '2':
            if selectisselect!='2':
                sql_list = Sql.objects.filter(Q(step=step),Q(is_select=selectisselect), Q(status=select)).order_by("-id")
            else:
                sql_list = Sql.objects.filter(Q(step=step), Q(status=select)).order_by("-id")
        else:
            if selectisselect!='2':
                sql_list = Sql.objects.filter(Q(step=step),Q(is_select=selectisselect)).order_by("-id")
            else:
                sql_list = Sql.objects.filter(Q(step=step)).order_by("-id")
    # 根据登录用户获取相关数据
    Step_dataqueryset = get_filiterStepdata(request)
    sql_list = sql_list.filter(step__in=Step_dataqueryset)

    paginator = Paginator(sql_list, NumberColumns)
    contacts = paginator.page(1)
    step_names = get_step_name(Step_dataqueryset)
    return render(request, "./main/sql.html", {"sqls": contacts,"selectstep":step_name,"selectdb_remark":selectdb_remark,"selectisselect":selectisselect,\
                                                   "select":select,"step_names": step_names,"db_remarks":db_remarks})

@login_required
def Nosql(request):
    step_name = request.GET.get("step_name")
    #print (step_name)
    selectisselect = request.GET.get("selectisselect")
    select = request.GET.get("select")
    checkedenv_ids = request.GET.get("checkedenv_ids")
    try:
        if step_name == "0":
            if select != '2':
                if selectisselect != '2':
                    Nosql_list = NoSql.objects.filter(Q(is_select=selectisselect), Q(status=select)).order_by("-id")
                else:
                    Nosql_list = NoSql.objects.filter(Q(status=select)).order_by("-id")
            else:
                if selectisselect != '2':
                    Nosql_list = NoSql.objects.filter(Q(is_select=selectisselect)).order_by("-id")
                else:
                    Nosql_list = NoSql.objects.filter().order_by("-id")
        else:
            # 得到外键数据
            step = Step.objects.get(step_name=step_name)
            if select != '2':
                if selectisselect != '2':
                    Nosql_list = NoSql.objects.filter(Q(step=step), Q(is_select=selectisselect), Q(status=select)).order_by("-id")
                else:
                    Nosql_list = NoSql.objects.filter(Q(step=step), Q(status=select)).order_by("-id")
            else:
                if selectisselect != '2':
                    Nosql_list = NoSql.objects.filter(Q(step=step), Q(is_select=selectisselect)).order_by("-id")
                else:
                    Nosql_list = NoSql.objects.filter(Q(step=step)).order_by("-id")
    except:
        Nosql_list=NoSql.objects.all().order_by("-id")
    # 根据登录用户获取相关数据
    Step_dataqueryset = get_filiterStepdata(request)
    Nosql_list = Nosql_list.filter(step__in=Step_dataqueryset)
    paginator=Paginator(Nosql_list,NumberColumns)
    page=request.GET.get("page")
    try:
        contacts=paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts=paginator.page(paginator.num_pages)
    response={"Nosqls":contacts}
    step_names = get_step_name(Step_dataqueryset)

    if step_names!=None:
        response["step_names"]=step_names
    if step_name!=None:
        response["selectstep"]=step_name
    else:
        step_name = '0'
        response["selectstep"] = step_name
    if selectisselect!=None:
        response["selectisselect"]=selectisselect
    else:
        selectisselect = '2'
        response["selectisselect"] = selectisselect
    if select!=None:
        response["select"]=select
    else:
        select = '2'
        response["select"] = select
    if checkedenv_ids!=None:
        response["checkedenv_ids"] = checkedenv_ids
    else:
        response["checkedenv_ids"]=None
    return render(request, "./main/Nosql.html",response)

@login_required
def Nosql_add_data(request):
    step_name=request.POST.get("step_name")
    Nosql_dataType=request.POST.get("Nosql_dataType")
    isselect=request.POST.get("isselect")
    variable = request.POST.get("variable")
    Nosql = request.POST.get("Nosql")
    Nosql_condition = request.POST.get("Nosql_condition")
    remake=request.POST.get('remake')
    status = request.POST.get('status')

    #得到外键数据
    step=Step.objects.get(step_name=step_name)
    if isselect==None:
        isselect=0
        variable=""
    else:
        isselect = 1
    if status!=None:
        NoSql.objects.create(Nosql_dataType=Nosql_dataType,is_select=isselect,variable=variable,Nosql=Nosql,Nosql_condition=Nosql_condition,remake=remake,status=1,step=step)
    else:
        NoSql.objects.create(Nosql_dataType=Nosql_dataType,is_select=isselect,variable=variable,Nosql=Nosql,Nosql_condition=Nosql_condition,remake=remake,status=0,step=step)
    # 根据登录用户获取相关数据
    Step_dataqueryset = get_filiterStepdata(request)
    contacts = get_firstPagefiliterdata(NoSql, Step_dataqueryset)
    step_names = get_step_name(Step_dataqueryset)
    return render(request, "./main/Nosql.html", {"Nosqls":contacts,"step_names": step_names})

@login_required
def Nosql_edit_data(request):
    Nosql_id = request.POST.get("id")
    step_name = request.POST.get("step_name")
    Nosql_dataType = request.POST.get("Nosql_dataType")
    isselect = request.POST.get("isselect")
    variable = request.POST.get("variable")
    Nosql = request.POST.get("Nosql")
    Nosql_condition = request.POST.get("Nosql_condition")
    remake = request.POST.get('remake')
    status = request.POST.get('status')

    # 得到外键数据
    step = Step.objects.get(step_name=step_name)
    if isselect == None:
        isselect = 0
        variable = ""
    else:
        isselect = 1
    if status!=None:
        NoSql.objects.filter(id=Nosql_id).update(Nosql_dataType=Nosql_dataType,is_select=isselect,variable=variable,Nosql=Nosql,Nosql_condition=Nosql_condition,remake=remake,status=1,step=step)
    else:
        NoSql.objects.filter(id=Nosql_id).update(Nosql_dataType=Nosql_dataType,is_select=isselect,variable=variable,Nosql=Nosql,Nosql_condition=Nosql_condition,remake=remake,status=0,step=step)
    # 根据登录用户获取相关数据
    Step_dataqueryset = get_filiterStepdata(request)
    contacts = get_firstPagefiliterdata(NoSql, Step_dataqueryset)
    step_names = get_step_name(Step_dataqueryset)
    return render(request, "./main/Nosql.html", {"Nosqls": contacts, "step_names": step_names})

@login_required
def Nosql_delete_data(request):
    Nosql_ids = request.POST.get("id")
    Nosql_ids=Nosql_ids.split(',')
    # 第一个传过来的值为None字符串 不需要
    Nosql_ids = Nosql_ids[1:]

    # 批量删除
    idstring = ','.join(Nosql_ids)
    NoSql.objects.extra(where=['id IN (' + idstring + ')']).delete()
    # 根据登录用户获取相关数据
    Step_dataqueryset = get_filiterStepdata(request)
    contacts = get_firstPagefiliterdata(NoSql, Step_dataqueryset)
    step_names = get_step_name(Step_dataqueryset)
    return render(request, "./main/Nosql.html", {"Nosqls": contacts, "step_names": step_names})

@login_required
def Nosql_search_name(request):
    step_name = request.GET.get("step_name")
    selectisselect = request.GET.get("selectisselect")
    select = request.GET.get("select")

    if step_name=="0":
        if select != '2':
            if selectisselect!='2':
                Nosql_list = NoSql.objects.filter(Q(is_select=selectisselect), Q(status=select)).order_by("-id")
            else:
                Nosql_list = NoSql.objects.filter( Q(status=select)).order_by("-id")
        else:
            if selectisselect!='2':
                Nosql_list = NoSql.objects.filter(Q(is_select=selectisselect)).order_by("-id")
            else:
                Nosql_list = NoSql.objects.filter().order_by("-id")
    else:
        # 得到外键数据
        step = Step.objects.get(step_name=step_name)
        if select != '2':
            if selectisselect!='2':
                Nosql_list = NoSql.objects.filter(Q(step=step),Q(is_select=selectisselect), Q(status=select)).order_by("-id")
            else:
                Nosql_list = NoSql.objects.filter(Q(step=step), Q(status=select)).order_by("-id")
        else:
            if selectisselect!='2':
                Nosql_list = NoSql.objects.filter(Q(step=step),Q(is_select=selectisselect)).order_by("-id")
            else:
                Nosql_list = NoSql.objects.filter(Q(step=step)).order_by("-id")
    # 根据登录用户获取相关数据
    Step_dataqueryset = get_filiterStepdata(request)
    Nosql_list = Nosql_list.filter(step__in=Step_dataqueryset)
    paginator = Paginator(Nosql_list, NumberColumns)
    contacts = paginator.page(1)
    step_names = get_step_name(Step_dataqueryset)
    return render(request, "./main/Nosql.html", {"Nosqls": contacts,"selectstep":step_name,"selectisselect":selectisselect,\
                                                   "select":select,"step_names": step_names})

#创建任务表
def create_task(case_ids,task_name,remark):
    for case_id in case_ids:
        case_data=Case.objects.filter(id=case_id).values("case_name","api")[0]
        # 得到外键数据
        case = Case.objects.get(id=case_id)
        Task.objects.create(task_name=task_name,case=case,remark=remark,status=0)
#用例生成脚本
#得到根据用例id拿到数据
def get_py_data(case_ids,testcasedir,task_name):
    #插入任务表的db和db_remark
    db=set([])
    db_remark=set([])
    str=','
    for case_id in case_ids:
        case_data=Case.objects.filter(id=case_id).values("case_name","api","case_desc")[0]
        # 得到外键数据
        case = Case.objects.get(id=case_id)
        step_list_data=Step.objects.filter(case=case,status=1).values("id","step_name","method","params","headers","files","assert_response","api_dependency","step_desc")
        for step_data in step_list_data:
            #得到外键数据
            step = Step.objects.get(id=step_data['id'])
            #sql数据
            sql_list_data=Sql.objects.filter(step=step,status=1).values("sql_condition","is_select","variable","sql","db","db_remark")
            #将数据用到的几个数据库id和连接名写入任务表
            for sql_data in sql_list_data:
                db.add(sql_data['db'])
                db_remark.add(sql_data['db_remark'])

            step_data['sql_list_data']=sql_list_data

            # Nosql数据
            nosql_list_data = NoSql.objects.filter(step=step, status=1).values("Nosql_dataType","Nosql_condition", "is_select", "variable",
                                                                           "Nosql")
            step_data['sql_list_data'] = sql_list_data
            step_data['nosql_list_data'] = nosql_list_data
        case_data["step_list_data"]=step_list_data
        make_testcase=Make_testcase(testcasedir,case_data)
        #print (case_data)
    # 将数据用到的几个数据库id和连接名写入任务表
    dbstr=str.join(db)
    db_remarkstr=str.join(db_remark)
    Task.objects.filter(task_name=task_name).update(db=dbstr,db_remark=db_remarkstr)
#判断是不是windows,在task目录下创建本次任务目录，再创建case
def crate_task(task_name):
    if os.name=='nt':
        task_dir=os.getcwd()+r"\task"
        task_name=task_dir+r"/"+task_name
        testcase=task_name+r"\testcase"
        report=task_name+r"\report"
    else:
        task_dir = os.getcwd() + r"/task"
        task_name = task_dir + r"/" + task_name
        testcase = task_name + r"/testcase"
        report = task_name + r"/report"
    create_dir(task_name)
    create_dir(testcase)
    create_dir(report)
    #创建一个初始化文件__init__.py
    filename=testcase+"/__init__.py"
    create_file(filename)
    return testcase
#生成脚本
@login_required
def make_case_data(request):
    case_ids = request.POST.get("id")
    task_name=request.POST.get("task_name")
    remark=request.POST.get("remark")
    task_name+="---"+str((uuid.uuid1()))
    code = len(Task.objects.filter(task_name=task_name).values())

    # 不重复则新增数据
    if code == 0:
        case_ids=case_ids.split(',')
        #print(case_ids)
        #第一个传过来的值为None字符串 不需要
        case_ids=case_ids[1:]
        #print (case_ids)

        # 校验生成任务接口必须含有用例
        code = db.checkTask(case_ids)
        if code == -1:
            codeMessage = "接口必须包含至少一个用例，生成脚本失败"
        else:
            #创建任务表
            create_task(case_ids,task_name,remark)
            #创建对应目录
            testcasedir=crate_task(task_name)
            #整合数据
            get_py_data(case_ids,testcasedir,task_name)
            codeMessage = ""
    # 重复则不新增数据
    else:
        codeMessage = "任务名重复，生成脚本失败"

    # 根据用户过滤数据权限
    filiterdata = get_filiterdata(request)
    Case_list = Case.objects.all().order_by("-id")
    Case_list = Case_list.filter(Modules__in=filiterdata)
    paginator = Paginator(Case_list, NumberColumns)
    contacts = paginator.page(1)

    # 得到列表项目名
    project_listnames = filter_project_listnames(Case_list)
    #把项目名和用例列表数据打包
    contactszip = zip(contacts, project_listnames)
    # 根据用户过滤数据权限
    filiterdata = get_filiterdata(request)
    project_names = get_project_name(filiterdata)
    project_name = project_names[0]

    modules_names = get_modules_name(project_name,filiterdata)
    return render(request, "./main/case.html",
                  {"cases": contactszip, "modules_names": modules_names, "project_names": project_names,"casees":contacts,"code":code,"codeMessage":codeMessage})

#得到环境和数据库的描述和邮件
@login_required
def get_env_database_desc(request):
    env_descs = []
    db_remarks=[]
    subjects=[]
    Nosqldb_descs=[]

    #环境
    startenv_descs = Environment.objects.values("env_desc")
    for i in range(len(startenv_descs)):
        env_descs.append(startenv_descs[i]['env_desc'])
    #nosql数据库
    startNosqldb_descs = NosqlDb.objects.values("NosqlDb_desc")
    for i in range(len(startNosqldb_descs)):
        Nosqldb_descs.append(startNosqldb_descs[i]['NosqlDb_desc'])
    #通过驱动的代码换成通过接口
    '''
    startdb_remarks = Database.objects.values("db_remark")
    for i in range(len(startdb_remarks)):
        db_remarks.append(startdb_remarks[i]['db_remark'])
    '''
    #拿到redis

    # 邮件
    start_subjects = Email.objects.values("subject")
    for i in range(len(start_subjects)):
        subjects.append(start_subjects[i]['subject'])
    return env_descs,Nosqldb_descs,db_remarks,subjects
#定时任务
@login_required
def task(request):
    env_descs,Nosqldb_descs,db_remarks,subjects=get_env_database_desc(request)
    task_name = request.GET.get("task_name")
    checkedenv_ids = request.GET.get("checkedenv_ids")
    try:
        data_list = Task.objects.filter(Q(task_name__contains=task_name)).values("task_name","task_run_time_regular","db_remark","env_desc","failcount","remark","status","subject","Nosqldb_desc").distinct().order_by('task_name')
    except:
        data_list = Task.objects.values("task_name","task_run_time_regular","db_remark","env_desc","failcount","remark","status","subject","Nosqldb_desc").distinct().order_by('task_name')
    paginator=Paginator(data_list,NumberColumns)
    page=request.GET.get("page")
    try:
        contacts=paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts=paginator.page(paginator.num_pages)
    response={"tasks":contacts}
    #project_names = get_project_name()
    if task_name!=None:
        response["task_name"]=task_name
    if env_descs!=None:
        response["env_descs"]=env_descs
    if Nosqldb_descs!=None:
        response["Nosqldb_descs"]=Nosqldb_descs
    if db_remarks!=None:
        response["db_remarks"]=db_remarks
    if subjects!=None:
        response["subjects"]=subjects
    if checkedenv_ids!=None:
        response["checkedenv_ids"] = checkedenv_ids
    else:
        response["checkedenv_ids"]=None
    return render(request, "./main/task.html",response)

#删除任务目录以及文件
def rm_task(task_name):
    #if os.name == 'nt':
    task_dir=os.getcwd()+r"/task/"+task_name
    if os.path.exists(task_dir):
        shutil.rmtree(task_dir)
@login_required
def tasks_delete_data(request):
    task_names = request.POST.get("task_names")
    env_descs,Nosqldb_descs,db_remarks, subjects = get_env_database_desc(request)
    #print (task_names)
    task_names=task_names.split(',')
    # 第一个传过来的值为None字符串 不需要
    task_names = task_names[1:]

    for task_name in task_names:
        if task_name!="":
            # 删除任务目录以及文件
            rm_task(task_name)
            Task.objects.filter(task_name=task_name).delete()

    # 得到一页数据
    data_list = Task.objects.values("task_name","task_run_time_regular","db_remark","env_desc","failcount","remark","status","subject","Nosqldb_desc").distinct().order_by('task_name')
    paginator = Paginator(data_list, NumberColumns)
    contacts = paginator.page(1)
    return render(request, "./main/task.html", {"tasks": contacts,"env_descs":env_descs,"subjects":subjects,"Nosqldb_descs":Nosqldb_descs})

@login_required
def task_search_name(request):
    task_name = request.GET.get("task_name")
    env_descs,Nosqldb_descs, db_remarks, subjects = get_env_database_desc(request)
    data_list = Task.objects.filter(Q(task_name__contains=task_name)).values("task_name","task_run_time_regular","db_remark","env_desc","failcount","remark","status","subject","Nosqldb_desc").distinct().order_by('task_name')
    # 得到一页数据
    paginator = Paginator(data_list, NumberColumns)
    contacts = paginator.page(1)
    return render(request, "./main/task.html", {"tasks": contacts,"task_name":task_name,"env_descs":env_descs,"subjects":subjects,"Nosqldb_descs":Nosqldb_descs})
#拼接ip和启动数据库对象
@login_required
def get_ip_database(request,task_name,env_desc,nosqldb_desc):
    #环境
    env_list=Environment.objects.filter(env_desc=env_desc).values("env_ip","env_host","env_port")
    if env_list[0]['env_ip'] != "":
        if env_list[0]['env_port'] != "":
            env_ip = "http://{host}:{port}".format(host=env_list[0]['env_ip'], port=env_list[0]['env_port'])
        else:
            env_ip = "http://{host}".format(host=env_list[0]['env_ip'])
    else:
        if env_list[0]['env_port'] != "":
            env_ip = "http://{host}:{port}".format(host=env_list[0]['env_host'], port=env_list[0]['env_port'])
        else:
            env_ip = "http://{host}".format(host=env_list[0]['env_host'])

    #需要启动的开发数据库
    db={}
    db_list=[]
    task_data=Task.objects.filter(task_name=task_name).values('db')
    dbstr=task_data[0]['db']
    db_list=dbstr.split(',')
    if db_list!=['']:
        for i in db_list:
            data_list=Db.objects.filter(id=i).values("db_type","db_ip","db_port","db_user","db_password","db_name")
            #mysql
            if data_list[0]['db_type']=='0':
                databaseobj=sqldbDatabase(data_list[0]['db_ip'],data_list[0]['db_port'],data_list[0]['db_user'],data_list[0]['db_password'],data_list[0]['db_name'])
            #sql server
            else:
                databaseobj =sqldbDatabase(data_list[0]['db_ip'], data_list[0]['db_user'], data_list[0]['db_password'],
                              data_list[0]['db_name'])
            db[i]=databaseobj
    else:
        db=None


    #Nosql数据库
    if nosqldb_desc=="":
        redis=None
    else:
        NosqlDbresult = NosqlDb.objects.filter(NosqlDb_desc=nosqldb_desc).values("host", "port", "password")
        host=NosqlDbresult[0]['host']
        if NosqlDbresult[0]['port']=="":
            port=6379
        else:
            port=NosqlDbresult[0]['port']
        if NosqlDbresult[0]['password']=="":
            password=None
        else:
            password=NosqlDbresult[0]['password']
        redis=Redis(host,port,password)

    create_db(db,env_ip,redis)

#写入定时任务数据
@login_required
def write_task(request,task_name,env_desc,nosqldb_desc,failcount,schedule,status,email_data):
    #环境
    env_id=Environment.objects.filter(env_desc=env_desc).values("id")[0]['id']
    # Nosql数据库
    if nosqldb_desc!="":
        Nosqldb_id=NosqlDb.objects.filter(NosqlDb_desc=nosqldb_desc).values("id")[0]['id']
    #不使用数据库
    else:
        Nosqldb_id=""
    if status != None:
        if email_data==None:
            Task.objects.filter(task_name=task_name).update(ip=env_id,Nosqldb=Nosqldb_id, failcount=failcount,
                                                        task_run_time_regular=schedule, status=1, env_desc=env_desc,Nosqldb_desc=nosqldb_desc)
        else:
            Task.objects.filter(task_name=task_name).update(ip=env_id,Nosqldb=Nosqldb_id, failcount=failcount,
                                                            task_run_time_regular=schedule, status=1, env_desc=env_desc,Nosqldb_desc=nosqldb_desc,
                                                            email=email_data['id'],subject=email_data['subject'])
    else:
        if email_data == None:
            Task.objects.filter(task_name=task_name).update(ip=env_id,Nosqldb=Nosqldb_id, failcount=failcount,
                                                        task_run_time_regular=schedule, status=0, env_desc=env_desc,Nosqldb_desc=nosqldb_desc)
        else:
            Task.objects.filter(task_name=task_name).update(ip=env_id,Nosqldb=Nosqldb_id, failcount=failcount,
                                                            task_run_time_regular=schedule, status=0, env_desc=env_desc,Nosqldb_desc=nosqldb_desc,
                                                            email=email_data['id'],subject=email_data['subject'])

#执行任务
@login_required
def task_run(request):
    task_name=request.POST.get("task_name")
    env_desc = request.POST.get("env_desc")
    #database_desc = request.POST.get("database_desc")
    nosqldb_desc = request.POST.get("Nosqldb_desc")
    subject = request.POST.get("subject")
    # 修改失败重跑的次数
    failcount=request.POST.get("failcount")
    #日程表
    schedule=request.POST.get('schedule')
    #状态
    status = request.POST.get('status')

    env_descs,Nosqldb_descs, db_remarks, subjects = get_env_database_desc(request)

    #如果要发送邮件拿到邮件配置数据
    if subject!=None:
        email_data=Email.objects.filter(subject=subject).values('id','sender','receivers','host_dir','email_port','username','passwd','Headerfrom','Headerto','subject')[0]
        #邮箱密码解密
        email_data['passwd']=base64.b64decode(email_data['passwd']).decode()
    else:
        email_data=None

    #选择一次性执行还是配置定时任务
    if schedule==None:
        #拼接ip
        get_ip_database(request,task_name,env_desc,nosqldb_desc)
        t = Thread(target=interface, args=(task_name, failcount, email_data))
        t.start()
    else:
        write_task(request,task_name,env_desc,nosqldb_desc,failcount,schedule,status,email_data)
        job = Job(task_name, schedule)
        if status != None:
            #新建任务
            job.create_job(request,env_desc,nosqldb_desc,failcount,subject)
        else:
            job.delete_job()
    search_task_name=None
    try:
        data_list = Task.objects.filter(Q(task_name__contains=search_task_name)).values("task_name","task_run_time_regular","env_desc","failcount","remark","status","subject","Nosqldb_desc").distinct().order_by('task_name')
    except:
        data_list = Task.objects.values("task_name","task_run_time_regular","env_desc","failcount","remark","status","subject","Nosqldb_desc").distinct().order_by('task_name')
    paginator=Paginator(data_list,NumberColumns)
    page=request.GET.get("page")
    try:
        contacts=paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts=paginator.page(paginator.num_pages)
    response={"tasks":contacts}
    #project_names = get_project_name()
    if search_task_name!=None:
        response["search_task_name"]=search_task_name
    if env_descs!=None:
        response["env_descs"]=env_descs
    if Nosqldb_descs != None:
        response["Nosqldb_descs"] = Nosqldb_descs
    if subjects!=None:
        response["subjects"]=subjects
    return render(request, "./main/task.html",response)
    #return JsonResponse(response)

#执行任务列表数据
@login_required
def task_status(request):
    task_name = request.GET.get("task_name")
    carrystatus=Task.objects.filter(task_name=task_name).values('carrystatus')[0]['carrystatus']
    #状态1运行中，2未开始，3已结束
    return JsonResponse({"carrystatus":carrystatus})

#执行任务列表
@login_required
def task_list(request):
    task_name = request.GET.get("task_name")
    # 状态1运行中，2未开始，3已结束
    carrystatus=Task.objects.filter(task_name=task_name).values('carrystatus')[0]['carrystatus']
    tasklist={"task_name":task_name,"carrystatus":carrystatus}
    tasklist['data']=[]
    taskdata=CarryTask.objects.filter(task_name=task_name).values('id','stepcountnow','stepcountall','create_time').order_by('-create_time')
    for i in range(len(taskdata)):
        if i==0:
            tasklist['stepcountnow'] = taskdata[i]['stepcountnow']
            tasklist['stepcountall'] = taskdata[i]['stepcountall']
        data = {}
        data['id']=taskdata[i]['id']
        data['stepcountnow']=taskdata[i]['stepcountnow']
        data['stepcountall'] = taskdata[i]['stepcountall']
        data['stepcountrate'] = int(data['stepcountnow']/data['stepcountall']*100)
        data['create_time'] = taskdata[i]['create_time'].strftime('%Y-%m-%d %H:%M:%S')
        tasklist['data'].append(data)

    return JsonResponse(tasklist)

#更改执行任务状态
@login_required
def update_task_status(request):
    task_name = request.GET.get("task_name")
    carrystatus = request.GET.get("carrystatus")
    try:
        Task.objects.filter(task_name=task_name).update(carrystatus=carrystatus)
        response={"code":0,"message":""}
    except:
        response = {"code": -1, "message": ""}

    return JsonResponse(response)

#得到定时任务数据
def get_task_data(request):
    task_name_list = Task.objects.filter(status=1).values("task_name","task_run_time_regular","env_desc","Nosqldb_desc","failcount","status",'email','subject').distinct().order_by('task_name')
    for i in range(len(task_name_list)):
        job = Job(task_name_list[i]['task_name'], task_name_list[i]['task_run_time_regular'])
        # 新建任务
        job.create_job(request,task_name_list[i]['env_desc'],task_name_list[i]['Nosqldb_desc'], task_name_list[i]['failcount'],task_name_list[i]['subject'])
#启动定时任务
@login_required
def start_timing_task(request):
    #启动全部定时任务
    get_task_data(request)

    env_descs,Nosqldb_descs, db_remarks, subjects = get_env_database_desc(request)
    task_name = None
    try:
        data_list = Task.objects.filter(Q(task_name__contains=task_name)).values("task_name","task_run_time_regular","env_desc","failcount","remark","status","subject","Nosqldb_desc").distinct().order_by('task_name')
    except:
        data_list = Task.objects.values("task_name","task_run_time_regular","env_desc","failcount","remark","status","subject","Nosqldb_desc").distinct().order_by('task_name')
    paginator=Paginator(data_list,NumberColumns)
    page=request.GET.get("page")
    try:
        contacts=paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts=paginator.page(paginator.num_pages)
    response={"tasks":contacts}
    #project_names = get_project_name()
    if task_name!=None:
        response["task_name"]=task_name
    if env_descs!=None:
        response["env_descs"]=env_descs
    if Nosqldb_descs!=None:
        response["Nosqldb_descs"]=Nosqldb_descs
    if subjects!=None:
        response["subjects"]=subjects

    return render(request, "./main/task.html",response)

#定时任务
@login_required
def htmlreport(request):
    task_name = request.GET.get("task_name")
    find_way = request.GET.get("find_way")
    carrytaskid=request.GET.get("carrytaskid")
    #查找日志
    if find_way=="findtextreport":
        id=carrytaskid
        if id==None:
            successmessage = "未生成有正确日志"
            failmessage = "未生成断言错误日志"
            print ("任务未被执行")
        else:
            lognames=CarryTask.objects.filter(id=id).values("successlogname","errorlogname")[0]
            successtext = lognames['successlogname']
            failtext = lognames['errorlogname']
            try:
                with open(successtext, 'r') as fp:
                    successmessage=fp.read()
                    fp.close()
            except:
                successmessage="未生成有正确日志"
            try:
                with open(failtext, 'r') as fp:
                    failmessage=fp.read()
                    fp.close()
            except:
                failmessage="未生成断言错误日志"
        return render(request, "../task/textreport.html",{"successmessage":successmessage,"failmessage":failmessage})
    #查找html
    elif find_way=="findhtmlreport":
        id = carrytaskid
        if id == None:
            htmlreport = "../task/nohtmlreport.html"
            print("任务未被执行")
        else:
            htmlnames = CarryTask.objects.filter(id=id).values("htmlreport")[0]
            htmlreport = htmlnames['htmlreport']
            try:
                with open(htmlreport, 'r') as fp:
                    fp.close()
            except:
                htmlreport="../task/nohtmlreport.html"
        return render(request, htmlreport)

#报告
@login_required
def report(request):
    response={}
    #接口数目
    casenumber=len(Case.objects.filter(status=1).all())
    #用例数目
    stepnumber=len(Step.objects.filter(status=1).all())
    #定时任务数目
    tasknumber=len(Task.objects.values('task_name').distinct())
    response['casenumber']=casenumber
    response['stepnumber'] = stepnumber
    response['tasknumber'] = tasknumber
    try:
        #通过数，失败数，错误断言数，总执行次数，错误率
        passnumber=len(LogAndHtmlfeedback.objects.filter(test_status=1))
        failnumber=len(LogAndHtmlfeedback.objects.filter(test_status=0))
        asserterrornumber = len(LogAndHtmlfeedback.objects.filter(test_status=2))
        carrynumber=passnumber+failnumber+asserterrornumber
        errorratio=(failnumber+asserterrornumber)*100/carrynumber
        errorratio=Decimal(errorratio).quantize(Decimal('0.00'))
        response['errorratio']=errorratio
        response['passnumber'] = passnumber
        response['failnumber'] = failnumber
        response['asserterrornumber'] = asserterrornumber

        #如果StatisticsData表有数据则更新，没有则新增一条
        if len(StatisticsData.objects.all())>=1:
            StatisticsData.objects.update(casenumber=casenumber,stepnumber=stepnumber, tasknumber=tasknumber, carrynumber=carrynumber,
                                          passnumber=passnumber, asserterrornumber=asserterrornumber, failnumber=failnumber,
                                          errorratio=errorratio*100)
        else:
            StatisticsData.objects.create(casenumber=casenumber,stepnumber=stepnumber, tasknumber=tasknumber, carrynumber=carrynumber,
                                          passnumber=passnumber, asserterrornumber=asserterrornumber, failnumber=failnumber,
                                          errorratio=errorratio*100)

        #获取今日反馈量
        date = now().date() + timedelta(days=0)  # 今天
        todayfeedbacknumber=len(LogAndHtmlfeedback.objects.filter(update_time__gte=date))
        response["todayfeedbacknumber"]=todayfeedbacknumber

        #取每日执行数量
        test_carryTaskid = CarryTask.objects.values("id").aggregate(id=Max('id'))['id']
        passnumberlist=[]
        failnumberlist=[]
        asserterrornumberlist=[]
        carrynumberlist=[]
        for i in range(test_carryTaskid,test_carryTaskid-5,-1):
            passnumberlist.append(len(LogAndHtmlfeedback.objects.filter(test_carryTaskid=i,test_status=1).all()))
            failnumberlist.append(len(LogAndHtmlfeedback.objects.filter(test_carryTaskid=i, test_status=0).all()))
            asserterrornumberlist.append(len(LogAndHtmlfeedback.objects.filter(test_carryTaskid=i, test_status=2).all()))
            carrynumberlist.append(len(LogAndHtmlfeedback.objects.filter(test_carryTaskid=i).all()))
        response['passnumberlist']=passnumberlist
        response['failnumberlist'] = failnumberlist
        response['asserterrornumberlist'] = asserterrornumberlist
        response['carrynumberlist'] = carrynumberlist

        #获取反馈信息
        feedbackmessages=LogAndHtmlfeedback.objects.values('test_step','test_response','test_status','update_time').order_by("-id")
        for i in range(len(feedbackmessages)):
            if feedbackmessages[i]['test_response']=="":
                feedbackmessages[i]['test_response']="非断言性异常"
            if feedbackmessages[i]['test_status']==1:
                feedbackmessages[i]['test_status']="pass"
            elif feedbackmessages[i]['test_status']==0:
                feedbackmessages[i]['test_status'] = "fail"
            else:
                feedbackmessages[i]['test_status'] = "asserterror"
        response['messages']=feedbackmessages

        #获取今日报错信息
        errorfeedbackmessages = LogAndHtmlfeedback.objects.filter(~Q(test_status=1),update_time__gte=date).values('test_step', 'test_response', 'test_status',
                                                             'update_time').order_by("-id")
        #print (errorfeedbackmessages)
        for i in range(len(errorfeedbackmessages)):
            if errorfeedbackmessages[i]['test_response'] == "":
                errorfeedbackmessages[i]['test_response'] = "接口内部错误"
            if errorfeedbackmessages[i]['test_status'] == 1:
                errorfeedbackmessages[i]['test_status'] = "pass"
            elif errorfeedbackmessages[i]['test_status'] == 0:
                errorfeedbackmessages[i]['test_status'] = "fail"
            else:
                errorfeedbackmessages[i]['test_status'] = "asserterror"
        response['errorsmessages'] = errorfeedbackmessages
        return render(request, "./main/report.html", response)
    except:
        response['errorratio'] = 0
        response['passnumber'] = 0
        response['failnumber'] = 0
        response['asserterrornumber'] = 0
        response["todayfeedbacknumber"] = 0
        response['passnumberlist'] = [0,0,0,0,0]
        response['failnumberlist'] = [0,0,0,0,0]
        response['asserterrornumberlist'] = [0,0,0,0,0]
        response['carrynumberlist'] = [0,0,0,0,0]
        return render(request, "./main/report.html",response)

#工具
@login_required
def formatJson(request):
    return render(request, "./main/formatJson.html")

@login_required
def functionhelp(request):
    dir = os.getcwd() + r"/public/expandfunction.py"
    with open(dir,"r",encoding='utf-8') as fp:
        responsemessage=fp.read()

    return render(request, "./main/functionhelp.html",{"responsemessage":str(responsemessage)})

