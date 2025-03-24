from django.contrib import admin
from .models import Project, ProjectType, ProjectInvitation, JoinRequest

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'start_date', 'end_date', 'category', 'status', 'project_color', 'members_count', 'created_at')
    search_fields = ('name', 'owner__username')
    list_filter = ('status', 'category', 'start_date', 'end_date', 'project_color')
    ordering = ('-created_at',)
    filter_horizontal = ('members',)

    def members_count(self, obj):
        return obj.members.count()
    members_count.short_description = "Members"

admin.site.register(Project, ProjectAdmin)


class ProjectTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(ProjectType, ProjectTypeAdmin)


class ProjectInvitationAdmin(admin.ModelAdmin):
    list_display = ('project', 'invited_user', 'status', 'created_at')
    search_fields = ('project__name', 'invited_user__username')
    list_filter = ('status', 'created_at')
    actions = ['accept_invitations']  # ✅ Bulk action

    def save_model(self, request, obj, form, change):
        previous_status = None
        if obj.pk:
            previous_status = ProjectInvitation.objects.get(pk=obj.pk).status

        super().save_model(request, obj, form, change)

        if obj.status == 'accepted' and (previous_status is None or previous_status != 'accepted'):
            obj.project.members.add(obj.invited_user)

    @admin.action(description="✅ Accept selected invitations and add members to projects")
    def accept_invitations(self, request, queryset):
        accepted_count = 0
        for invitation in queryset:
            if invitation.status != 'accepted':
                invitation.status = 'accepted'
                invitation.save()
                invitation.project.members.add(invitation.invited_user)
                accepted_count += 1
        self.message_user(request, f"{accepted_count} invitation(s) accepted and members added.")

admin.site.register(ProjectInvitation, ProjectInvitationAdmin)


class JoinRequestAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'status', 'created_at')
    search_fields = ('project__name', 'user__username')
    list_filter = ('status', 'created_at')
    actions = ['accept_requests']  # ✅ Bulk action

    @admin.action(description="✅ Accept selected join requests and add users to projects")
    def accept_requests(self, request, queryset):
        accepted_count = 0
        for join_request in queryset:
            if join_request.status != 'accepted':
                join_request.status = 'accepted'
                join_request.save()
                join_request.project.members.add(join_request.user)
                accepted_count += 1
        self.message_user(request, f"{accepted_count} join request(s) accepted and users added.")

admin.site.register(JoinRequest, JoinRequestAdmin)
