"""requestnew URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from request import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    #其他地址
    path('admin/', admin.site.urls),
    url('^index/$', views.get_index),
    url('^login_action/$', views.login_action),
    url('^first_page/$', views.first_page),
    url('^$',views.get_index),

    #测试项目
    url('project/$',views.project),
    url('^project_add_data/$', views.project_add_data),
    url('^project_edit_data/$', views.project_edit_data),
    url('^project_delete_data/$', views.project_delete_data),
    url('^project_search_name/$', views.project_search_name),
    #测试模块
    url('modules/$',views.modules),
    url('^modules_add_data/$', views.modules_add_data),
    url('^modules_edit_data/$', views.modules_edit_data),
    url('^modules_delete_data/$', views.modules_delete_data),
    url('^modules_search_name/$', views.modules_search_name),
    #测试用例
    url('case/$',views.case),
    url('^get_modules_name/$',views.get_modules),
    url('^case_add_data/$', views.case_add_data),
    url('^case_edit_data/$', views.case_edit_data),
    url('^case_delete_data/$', views.case_delete_data),
    url('^case_search_name/$', views.case_search_name),
    #测试步骤
    url('step/$',views.step),
    url('^step_add_data/$', views.step_add_data),
    url('^step_edit_data/$', views.step_edit_data),
    url('^step_copy_data/$', views.step_copy_data),
    url('^step_delete_data/$', views.step_delete_data),
    url('^step_search_name/$', views.step_search_name),
    #测试sql
    url('^sql/$',views.sql),
    url('^sql_add_data/$', views.sql_add_data),
    url('^sql_edit_data/$', views.sql_edit_data),
    url('^sql_delete_data/$', views.sql_delete_data),
    url('^sql_editDb/$', views.sql_editDb),
    url('^sql_search_name/$', views.sql_search_name),
    #测试Nosql
    url('^Nosql/$',views.Nosql),
    url('^Nosql_add_data/$', views.Nosql_add_data),
    url('^Nosql_edit_data/$', views.Nosql_edit_data),
    url('^Nosql_delete_data/$', views.Nosql_delete_data),
    url('^Nosql_search_name/$', views.Nosql_search_name),
    #环境配置
    url('^env/$',views.env),
    url('^env_add_data/$', views.env_add_data),
    url('^env_edit_data/$', views.env_edit_data),
    url('^env_delete_data/$', views.env_delete_data),
    url('^env_search_name/$', views.env_search_name),
    #邮箱配置
    url('^email/$',views.email),
    url('^email_add_data/$', views.email_add_data),
    url('^email_edit_data/$', views.email_edit_data),
    url('^email_delete_data/$', views.email_delete_data),
    url('^email_search_name/$', views.email_search_name),
    #数据库配置
    url('^database/$',views.database),
    url('^database_add_data/$', views.database_add_data),
    url('^database_edit_data/$', views.database_edit_data),
    url('^database_delete_data/$', views.database_delete_data),
    url('^database_search_name/$', views.database_search_name),

    #非关系数据库配置
    url('^NosqlDatabase/$',views.NosqlDatabase),
    url('^NosqlDatabase_add_data/$', views.NosqlDatabase_add_data),
    url('^NosqlDatabase_edit_data/$', views.NosqlDatabase_edit_data),
    url('^NosqlDatabase_delete_data/$', views.NosqlDatabase_delete_data),
    url('^NosqlDatabase_search_name/$', views.NosqlDatabase_search_name),

    #生成脚本
    url('^make_case_data/$', views.make_case_data),

    #定时任务
    url('^task/$', views.task),
    url('^tasks_delete_data/$', views.tasks_delete_data),
    url('^task_search_name/$', views.task_search_name),
    url('^task_run/$', views.task_run),
    url('^task_list/$', views.task_list),
    url('^update_task_status/$', views.update_task_status),
    url('^task_status/$', views.task_status),
    url('^start_timing_task/$', views.start_timing_task),

    #执行结果
    url('^htmlreport/$', views.htmlreport),

    #报告
    url('^report/$', views.report),

    #测试工具
    url('^formatJson/$', views.formatJson),
    url('^functionhelp/$', views.functionhelp),
]
