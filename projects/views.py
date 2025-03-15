from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import Project, ProjectType, ProjectAttachment, ProjectInvitation, JoinRequest
from .forms import ProjectForm

CustomUser = get_user_model()

# 📌 عرض جميع المشاريع مع الطلبات الواردة والمرسلة
@login_required
def project_list(request):
    if request.user.is_superuser:
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(owner=request.user) | Project.objects.filter(members=request.user)

    project_types = ProjectType.objects.all()
    sent_requests = JoinRequest.objects.filter(user=request.user)  
    received_requests = JoinRequest.objects.filter(project__owner=request.user, status='pending')

    for project in projects:
        project.update_progress()
        project.is_owner = project.owner == request.user  # ✅ تحديد إذا كان المستخدم هو المالك
        project.is_member = request.user in project.members.all()  # ✅ تحديد إذا كان المستخدم عضوًا

    return render(request, 'projects_list.html', {
        'projects': projects,
        'project_types': project_types,
        'sent_requests': sent_requests,
        'received_requests': received_requests
    })
# 📌 عرض الطلبات الواردة والمرسلة لكل مستخدم
@login_required
def project_requests(request):
    sent_requests = JoinRequest.objects.filter(user=request.user)  # الطلبات التي أرسلها المستخدم
    received_requests = JoinRequest.objects.filter(project__owner=request.user, status='pending')  # الطلبات التي تلقاها المالك

    return render(request, 'requests_overview.html', {
        'sent_requests': sent_requests,
        'received_requests': received_requests
    })

# 📌 عرض تفاصيل مشروع معين
@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    project.update_progress()

    if not request.user.is_superuser and project.owner != request.user and request.user not in project.members.all():
        messages.error(request, "You do not have permission to view this project.")
        return redirect('projects_list')

    members = project.members.all()
    is_owner = project.owner == request.user  # ✅ هل المستخدم هو المالك؟
    is_member = request.user in project.members.all()  # ✅ هل المستخدم عضو؟

    return render(request, 'project_detail.html', {
        'project': project,
        'members': members,
        'is_owner': is_owner,
        'is_member': is_member
    })

# 📌 إضافة مشروع جديد


@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user  
            project.save()
            form.save_m2m()

            # ✅ Save attachments if provided
            for file in request.FILES.getlist('attachments'):
                ProjectAttachment.objects.create(project=project, file=file)

            project.update_progress()

            # ✅ Store success message for redirect
            messages.success(request, "Project created successfully!")

            # ✅ طباعة للتحقق مما إذا كان `redirect()` يتم تنفيذه
            print("✅ Redirecting to projects_list")

            # ✅ Redirect to projects list directly without AJAX
            return redirect('projects_list')

    else:
        form = ProjectForm()

    return render(request, 'create_project.html', {'form': form})

@login_required
def update_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.user != project.owner and not request.user.is_superuser:
        messages.error(request, "You do not have permission to edit this project.")
        return redirect('projects_list')

    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            
            # 📩 تحديث المرفقات إن وجدت
            for file in request.FILES.getlist('attachments'):
                ProjectAttachment.objects.create(project=project, file=file)

            project.update_progress()
            messages.success(request, "Project updated successfully!")
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project)

    return render(request, 'update_project.html', {'form': form, 'project': project})

# 📌 حذف مشروع
@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if not request.user.is_superuser and project.owner != request.user:
        messages.error(request, "You do not have permission to delete this project.")
        return redirect('projects_list')
    
    project.delete()
    messages.success(request, "Project deleted successfully!")
    return redirect('projects_list')

# 📌 إرسال دعوة للانضمام إلى مشروع
@login_required
def send_invitation(request, project_id, user_id):
    project = get_object_or_404(Project, id=project_id)
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.user != project.owner:
       messages.error(request, "Only the project owner can send invitations.")
       return redirect('project_detail', project_id=project.id)
    
    if request.user != project.owner:
        messages.error(request, "Only the project owner can send invitations.")
        return redirect('project_detail', project_id=project.id)
    
    invitation, created = ProjectInvitation.objects.get_or_create(project=project, invited_user=user)
    
    if created:
        messages.success(request, "Invitation sent successfully!")
    else:
        messages.info(request, "Invitation already sent.")
    
    return redirect('project_detail', project_id=project.id)

# 📌 إرسال طلب انضمام إلى مشروع
@login_required
def send_join_request(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if JoinRequest.objects.filter(project=project, user=request.user).exists():
        messages.info(request, "You have already sent a request to join this project.")
    else:
        JoinRequest.objects.create(project=project, user=request.user)
        messages.success(request, "Join request sent successfully!")

    return redirect('projects_list')

# 📌 قبول أو رفض طلب انضمام
@login_required
def respond_to_join_request(request, request_id, response):
    join_request = get_object_or_404(JoinRequest, id=request_id, project__owner=request.user)

    if response == 'accept':
        join_request.status = 'accepted'
        join_request.project.members.add(join_request.user)
        messages.success(request, "User has been added to the project.")
    elif response == 'reject':
        join_request.status = 'rejected'
        messages.info(request, "Join request has been declined.")
    else:
        messages.error(request, "Invalid response.")
        return redirect('projects_list')

    join_request.save()
    return redirect('projects_list')

# 📌 قبول أو رفض دعوة
@login_required
def respond_to_invitation(request, invitation_id, response):
    invitation = get_object_or_404(ProjectInvitation, id=invitation_id, invited_user=request.user)

    if response == 'accept':
        invitation.status = 'accepted'
        invitation.project.members.add(request.user)
        messages.success(request, "You have joined the project!")
    elif response == 'reject':
        invitation.status = 'rejected'
        messages.info(request, "You have declined the invitation.")
    else:
        messages.error(request, "Invalid response.")
        return redirect('projects_list')
    
    invitation.save()
    return redirect('projects_list')
