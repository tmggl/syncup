from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Task, TaskUpdate, Project  
from .forms import TaskForm


# ✅ عرض لوحة التحكم Dashboard
@login_required
def dashboard_view(request):
    user = request.user

    # ✅ المشاريع التي يملكها أو يشارك فيها
    owned_projects = Project.objects.filter(owner=user)
    participated_projects = Project.objects.filter(members=user)

    # ✅ حساب الإحصائيات
    owned_projects_count = owned_projects.count()
    participated_projects_count = participated_projects.count()
    assigned_tasks_count = Task.objects.filter(assigned_to=user).count()
    pending_tasks_count = Task.objects.filter(assigned_to=user, status="pending").count()

    # ✅ جلب قائمة المهام الخاصة بالمستخدم
    tasks = Task.objects.filter(assigned_to=user)

    # ✅ جلب أقرب مهمة قادمة بعد الموافقة عليها (In Progress)
    upcoming_task = Task.objects.filter(
        assigned_to=user, status="in_progress"
    ).order_by('due_date').first()

    context = {
        'user': user,
        'owned_projects_count': owned_projects_count,
        'participated_projects_count': participated_projects_count,
        'assigned_tasks_count': assigned_tasks_count,
        'pending_tasks_count': pending_tasks_count,  # ✅ تمرير المهام المعلقة
        'tasks': tasks,
        'owned_projects': owned_projects,
        'participated_projects': participated_projects,
        'upcoming_task': upcoming_task,  # ✅ تمرير المهمة القادمة
    }

    return render(request, 'dashboard.html', context)

# ✅ عرض جميع المهام الخاصة بالمستخدم أو المشروع
@login_required
def task_list(request, project_id=None):
    """✅ عرض جميع المهام الخاصة بالمستخدم أو جميع المهام الخاصة بالمشروع"""
    if project_id:
        project = get_object_or_404(Project, id=project_id)

        # ✅ تحديد ما إذا كان المستخدم هو مالك المشروع
        is_owner = project.owner == request.user

        if is_owner:
            # ✅ إذا كان المستخدم هو مالك المشروع، يعرض جميع المهام المرتبطة بالمشروع
            tasks = Task.objects.filter(project=project)
        else:
            # ✅ إذا كان المستخدم موظفًا، يعرض فقط المهام المسندة إليه داخل المشروع
            tasks = Task.objects.filter(project=project, assigned_to=request.user)

    else:
        # ✅ إذا لم يكن هناك `project_id`، يتم عرض المهام المسندة إلى المستخدم فقط
        tasks = Task.objects.filter(assigned_to=request.user)
        is_owner = False  # ✅ لأنه لا يوجد مشروع معين

    return render(request, 'tasks_list.html', {
        'tasks': tasks,
        'project': project if project_id else None,
        'is_owner': is_owner,  # ✅ تمرير هذه القيمة للقالب لضبط العرض
    })

# ✅ عرض تفاصيل مهمة معينة
@login_required
def task_detail(request, task_id):
    """✅ عرض تفاصيل المهمة وتمكين المستخدم من الموافقة أو الرفض"""
    task = get_object_or_404(Task, id=task_id)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "accept":
            task.status = "in_progress"
            messages.success(request, "Task accepted. You can now start working on it.")
        elif action == "reject":
            task.status = "rejected"
            messages.warning(request, "You have rejected the task. The project manager will be notified.")
        task.save()

    return render(request, 'task_detail.html', {'task': task})


# ✅ إنشاء مهمة جديدة (مدير المشروع فقط)

@login_required
def create_task(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)

    if request.method == "POST":
        form = TaskForm(request.POST, request.FILES, user=request.user, selected_project=project)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.status = "pending"
            task.save()
            # ✅ رسالة النجاح مع رابط لقائمة المهام المرسلة
            success_message = mark_safe(
                'Task has been successfully created and assigned to the member. '
                '<a href="{0}" style="color:#2563eb; font-weight:600; text-decoration:underline;">View sent tasks</a>'.format(
                    reverse('sent_tasks')
                )
            )
            messages.success(request, success_message)
            return redirect('sent_tasks')  # ✅ إعادة التوجيه إلى المهام المرسلة

    else:
        form = TaskForm(user=request.user, selected_project=project)

    return render(request, 'create_task.html', {'form': form, 'project': project})


# ✅ تحديث حالة المهمة
@login_required
def update_task_status(request, task_id):
    """✅ تحديث حالة المهمة بواسطة المدير فقط"""
    task = get_object_or_404(Task, id=task_id, project__owner=request.user)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            task.save()
            messages.success(request, "Task status updated successfully. Project progress recalculated.")
        else:
            messages.error(request, "Invalid status.")

    return redirect('task_detail', task_id=task.id)


# ✅ حذف مهمة
@login_required
def delete_task(request, task_id):
    """✅ حذف مهمة بواسطة المدير فقط"""
    task = get_object_or_404(Task, id=task_id, project__owner=request.user)
    project_id = task.project.id
    task.delete()
    messages.success(request, "Task has been successfully deleted.")

    return redirect('task_list', project_id=project_id)


# ✅ قبول أو رفض المهمة من قبل المستخدم
@login_required
def respond_to_task(request, task_id, response):
    """✅ يسمح للعضو بقبول أو رفض المهمة"""
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)

    if response == "accept":
        task.status = "in_progress"
        messages.success(request, "Task accepted.")
    elif response == "reject":
        task.status = "rejected"
        messages.warning(request, "Task rejected.")

    task.save()
    return redirect('task_detail', task_id=task.id)


# ✅ View to display tasks sent by the project owner
@login_required
def sent_tasks(request):
    """✅ Display all tasks created by the current user as a project owner"""
    tasks = Task.objects.filter(project__owner=request.user).select_related('project', 'assigned_to').order_by('-created_at')


    return render(request, 'sent_tasks.html', {'tasks': tasks})

@login_required
def task_progress(request, task_id):
    """✅ السماح للموظف بمشاهدة المهام الخاصة به فقط، بينما يرى المالك جميع المهام في المشروع"""
    task = get_object_or_404(Task, id=task_id)

    # ✅ إذا كان المستخدم هو المالك، يمكنه رؤية جميع المهام
    if request.user == task.project.owner:
        is_owner = True
        task_updates = TaskUpdate.objects.filter(task=task).order_by('-uploaded_at')
    
    # ✅ إذا كان المستخدم هو الموظف الذي تم إسناد المهمة له
    elif request.user == task.assigned_to:
        is_owner = False
        task_updates = TaskUpdate.objects.filter(task=task).order_by('-uploaded_at')

    else:
        # ❌ منع أي مستخدم آخر من الوصول
        messages.error(request, "You do not have permission to view this task progress.")
        return redirect('tasks_list_by_project', project_id=task.project.id)

    return render(request, 'task_progress.html', {
        'task': task,
        'task_updates': task_updates,
        'is_owner': is_owner,
    })



@login_required
def upload_task_update(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == "POST":
        if "update_file" in request.FILES:  # ✅ التحقق من وجود الملف قبل الحفظ
            file = request.FILES["update_file"]
            description = request.POST.get("update_description", "")

            TaskUpdate.objects.create(
                task=task,
                file=file,
                description=description,
                uploaded_by=request.user
            )

            messages.success(request, "Task update uploaded successfully!")
        else:
            messages.error(request, "No file was uploaded!")

    return redirect('task_progress', task_id=task.id)
