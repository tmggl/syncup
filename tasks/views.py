from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Task, Project

# ✅ عرض لوحة التحكم Dashboard
@login_required
def dashboard_view(request):
    user = request.user

    # ✅ جلب المشاريع التي يملكها أو يشارك فيها
    owned_projects = Project.objects.filter(owner=user)
    participated_projects = Project.objects.filter(members=user)

    # ✅ حساب الإحصائيات
    owned_projects_count = owned_projects.count()
    participated_projects_count = participated_projects.count()
    assigned_tasks_count = Task.objects.filter(assignee=user).count()
    pending_tasks_count = Task.objects.filter(assignee=user, completed=False).count()

    # ✅ جلب قائمة المهام الخاصة بالمستخدم
    tasks = Task.objects.filter(assignee=user)

    context = {
        'user': user,
        'owned_projects_count': owned_projects_count,
        'participated_projects_count': participated_projects_count,
        'assigned_tasks_count': assigned_tasks_count,
        'pending_tasks_count': pending_tasks_count,  # ✅ تمرير المتغير الجديد
        'tasks': tasks,
        'owned_projects': owned_projects,
        'participated_projects': participated_projects,
    }
    
    return render(request, 'dashboard.html', context)  # ✅ يتوافق مع مسار القوالب


# ✅ عرض جميع المهام
@login_required
def task_list(request):
    tasks = Task.objects.all()
    return render(request, 'tasks_list.html', {'tasks': tasks})  # ✅ يتوافق مع مسار القوالب


# ✅ عرض تفاصيل مهمة معينة
@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'task_detail.html', {'task': task})  # ✅ يتوافق مع مسار القوالب


# ✅ تحديث حالة المهمة
@login_required
def update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')  # الحصول على الحالة الجديدة من الفورم
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            task.save()  # ✅ عند حفظ المهمة، سيتم استدعاء `update_progress` تلقائيًا من `save()` في `Task`
            messages.success(request, "تم تحديث حالة المهمة وتحديث نسبة التقدم في المشروع.")
        else:
            messages.error(request, "حالة غير صالحة.")

    return redirect('task_detail', task_id=task.id)
