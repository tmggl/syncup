from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from .forms import ProfileUpdateForm  
from django.contrib.auth.forms import PasswordChangeForm
from projects.models import JoinRequest  
from tasks.models import Task
from meetings.models import Meeting
from django.db.models import Q
from django.utils import timezone


# استيراد نموذج المستخدم المخصص
CustomUser = get_user_model()

# عرض الصفحة الرئيسية
def home_view(request):
    return render(request, 'home.html')

# تسجيل الدخول
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # توجيه المستخدم إلى لوحة التحكم بعد تسجيل الدخول

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # توجيه المستخدم بناءً على دوره
        else:
            messages.error(request, "اسم المستخدم أو كلمة المرور غير صحيحة", extra_tags='login')
    
    # تنظيف الرسائل القديمة حتى لا تتكرر من صفحات أخرى
    messages.get_messages(request).used = True
    
    return render(request, 'login.html')
# تسجيل الخروج
def logout_view(request):
    logout(request)
    return redirect('home')  #  يعيد المستخدم إلى الصفحة الرئيسية
# تسجيل حساب جديد
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)  # إضافة request.FILES لحفظ الصورة
        if form.is_valid():
            form.save()  # حفظ المستخدم بدون تسجيل الدخول تلقائيًا
            return redirect('registration_success')  # توجيه المستخدم إلى صفحة نجاح التسجيل
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})

# عرض صفحة نجاح التسجيل
def registration_success(request):
    return render(request, 'registration_success.html')# عرض قائمة المستخدمين (متاح فقط للمشرفين والخبراء)
@login_required
def users_list(request):
    if request.user.role != 'expert':
        return render(request, 'error.html', {'message': 'ليس لديك صلاحية لرؤية قائمة المستخدمين'})

    query = request.GET.get('search', '')
    users = CustomUser.objects.exclude(role='expert')  # منع الخبراء من رؤية خبراء آخرين
    if query:
        users = users.filter(username__icontains=query)

    return render(request, 'users_list.html', {'users': users, 'query': query})

# عرض لوحة التحكم بناءً على دور المستخدم



@login_required
def dashboard_view(request):
    user = request.user
    today = timezone.localdate()

    
    pending_tasks_count = Task.objects.filter(
        assigned_to=user,
        status__in=['new', 'pending', 'in_progress', 'urgent'],
        due_date__isnull=False,
        due_date__gte=today
    ).count()

    
    completed_tasks_count = Task.objects.filter(
        assigned_to=user,
        status='completed'
    ).count()

    #
    upcoming_task = Task.objects.filter(
        assigned_to=user,
        due_date__isnull=False,
        due_date__gte=today
    ).order_by('due_date').first()

    upcoming_meeting = Meeting.objects.filter(
        Q(participants=user) | Q(expert=user),
        date__isnull=False,
        date__gte=today
    ).order_by('date', 'time').first()

    context = {
        'user': user,
        'is_expert': user.role == 'expert',
        'pending_tasks_count': pending_tasks_count,
        'completed_tasks_count': completed_tasks_count,
        'upcoming_task': upcoming_task,
        'upcoming_meeting': upcoming_meeting,
    }

    if user.role == 'expert':
        return render(request, 'expert_dashboard.html', context)

    return render(request, 'dashboard.html', context)
@login_required
def expert_dashboard_view(request):
    return render(request, 'expert_dashboard.html')  # 

@login_required
def join_requests_view(request):
    """عرض طلبات الانضمام للمشاريع التي يديرها الخبير."""
    join_requests = JoinRequest.objects.filter(project__owner=request.user, status='pending')
    return render(request, 'join_requests.html', {'join_requests': join_requests})

# التحقق من توفر اسم المستخدم
def check_username(request):
    username = request.GET.get('value', '')
    exists = CustomUser.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})

# التحقق من توفر رقم الهاتف
def check_phone_number(request):
    phone_number = request.GET.get('value', '')
    exists = CustomUser.objects.filter(phone_number=phone_number).exists()
    return JsonResponse({'exists': exists})

@login_required
def expert_special_feature_view(request):
    return render(request, 'expert_feature.html')  # 



@login_required
def settings_view(request):
    user = request.user  # جلب بيانات المستخدم الحالية

    if request.method == "POST":
        
        if "profile_image" in request.FILES:
            user.profile_image = request.FILES["profile_image"]
            user.save()
            return JsonResponse({"success": True, "image_url": user.profile_image.url})  # 

        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        password_form = PasswordChangeForm(user, request.POST)

        if "change_password" in request.POST:  # تغيير كلمة المرور
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password updated successfully!")
                return redirect("settings")

        elif form.is_valid():  # تحديث بيانات الحساب
            form.save()
            messages.success(request, "Account details updated successfully!")
            return redirect("settings")

    else:
        form = ProfileUpdateForm(instance=user)
        password_form = PasswordChangeForm(user)

    return render(request, "settings.html", {"form": form, "password_form": password_form, "user": user})

@login_required
def edit_expert_bio(request):
    if request.user.role != 'expert':
        return redirect('dashboard')

    if request.method == 'POST':
        short_bio = request.POST.get('short_bio', '').strip()[:15]
        full_bio = request.POST.get('full_bio', '').strip()

        request.user.short_bio = short_bio
        request.user.full_bio = full_bio
        request.user.save()

        messages.success(request, "Your expert profile has been updated successfully.")
        return redirect('edit_expert_bio')

    return render(request, 'edit_expert_bio.html')