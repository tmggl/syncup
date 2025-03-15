from django.contrib import admin
from .models import Project, ProjectType, ProjectInvitation, JoinRequest

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'start_date', 'end_date', 'category', 'status', 'project_color', 'members_count', 'created_at')  # ✅ تحديث العرض
    search_fields = ('name', 'owner__username')
    list_filter = ('status', 'category', 'start_date', 'end_date', 'project_color')  # ✅ إضافة `project_color`
    ordering = ('-created_at',)

    def members_count(self, obj):
        return obj.members.count()
    members_count.short_description = "Members"

admin.site.register(Project, ProjectAdmin)

class ProjectTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(ProjectType, ProjectTypeAdmin)

class ProjectInvitationAdmin(admin.ModelAdmin):
    list_display = ('project', 'invited_user', 'status', 'created_at')  # ✅ استبدال `user` بـ `invited_user`
    search_fields = ('project__name', 'invited_user__username')  # ✅ التأكد من استخدام `invited_user`
    list_filter = ('status', 'created_at')

admin.site.register(ProjectInvitation, ProjectInvitationAdmin)

class JoinRequestAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'status', 'created_at')
    search_fields = ('project__name', 'user__username')
    list_filter = ('status', 'created_at')

admin.site.register(JoinRequest, JoinRequestAdmin)
