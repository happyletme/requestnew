from django.contrib import admin
from request.models import Project,Modules,User
from django.db.models import Q


# Register your models here.
class ProjectPostAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        # 自定义操作
        if change:
            isRepeat=len(Project.objects.filter(~Q(id=obj.id), project_name=obj.project_name).values())
        else:
            isRepeat = len(Project.objects.filter( project_name=obj.project_name).values())
        # 不重复则更新数据
        if isRepeat == 0:
            obj.save()
            msg = u'项目操作成功了耶'
        else:
            msg = u'项目名重复，操作失败了呦'
        self.message_user(request, msg)
    list_display = ('project_name','project_desc','status')
    list_per_page = 50



class ModulesPostAdmin(admin.ModelAdmin):
    def Tester(self, obj):
        return [a.username for a in obj.Testers.all()]
    def save_model(self, request, obj, form, change):
        project = Project.objects.get(project_name=obj.Project)
        # 自定义操作
        if change:
            isRepeat=len(Modules.objects.filter(~Q(id=obj.id), Modules_name=obj.Modules_name,Project=project).values())
        else:
            isRepeat = len(Modules.objects.filter( Modules_name=obj.Modules_name, Project=project).values())
        # 不重复则更新数据
        if isRepeat == 0:
            obj.save()
            msg = u'模块操作成功了耶'
        else:
            msg = u'同一个项目下操作相同模块名，操作失败了呦'
        self.message_user(request, msg)
    list_display = ('Modules_name','Project', 'Developer','Tester','status','Modules_desc')
    fk_fields = ('Project')
    filter_horizontal = ('Testers',)
    list_per_page = 50

admin.site.register(Modules, ModulesPostAdmin)
admin.site.register(Project, ProjectPostAdmin)