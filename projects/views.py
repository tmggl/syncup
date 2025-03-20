from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import Project, ProjectType, ProjectAttachment, ProjectInvitation, JoinRequest
from .forms import ProjectForm
from django.db.models import Q

CustomUser = get_user_model()

# 📌 عرض جميع المشاريع مع الطلبات الواردة والمرسلة
@login_required
def project_list(request):
    if request.user.is_superuser:
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(owner=request.user) | Project.objects.filter(members=request.user)

    project_types = ProjectType.objects.all()
    sent_requests = ProjectInvitation.objects.filter(project__owner=request.user).select_related('invited_user', 'project')
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
    sent_requests = ProjectInvitation.objects.filter(project__owner=request.user).select_related('invited_user', 'project')
    received_requests = JoinRequest.objects.filter(project__owner=request.user, status='pending')  # الطلبات التي تلقاها المالك

    return render(request, 'requests_overview.html', {
        'sent_requests': sent_requests,
        'received_requests': received_requests
    })

# 📌 عرض تفاصيل مشروع معين

CustomUser = get_user_model()

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    project.update_progress()

    if not request.user.is_superuser and project.owner != request.user and request.user not in project.members.all():
        messages.error(request, "You do not have permission to view this project.")
        return redirect('projects_list')

    members = project.members.all()
    is_owner = project.owner == request.user
    is_member = request.user in project.members.all()

    pending_requests = []
    if is_owner:
        pending_requests = JoinRequest.objects.filter(project=project, status='pending')

    user_join_request = None
    if not is_owner and not is_member:
        user_join_request = JoinRequest.objects.filter(project=project, user=request.user, status='pending').first()

    # ✅ تمرير قائمة المستخدمين المتاحين لدعوتهم (باستثناء المالك والأعضاء الحاليين)
    available_users = CustomUser.objects.exclude(id__in=project.members.values_list('id', flat=True)).exclude(id=project.owner.id)

    # ✅ جلب الملفات الرئيسية للمشروع (تظهر في الأعلى)
    main_files = ProjectAttachment.objects.filter(project=project, is_main_file=True)

    # ✅ جلب التحديثات الخاصة بالمشروع (التي تم رفعها لاحقًا)
    update_files = ProjectAttachment.objects.filter(project=project, is_main_file=False).order_by('-uploaded_at')

    # ✅ إضافة تحديث جديد (رفع ملف)
    if request.method == "POST" and request.FILES.get("new_file"):
        file = request.FILES["new_file"]
        file_name = request.POST.get("file_name", file.name)  # اسم الملف يدخله المستخدم، وإذا لم يدخل يُستخدم الاسم الأصلي
        description = request.POST.get("description", "")  # الوصف اختياري

        # ✅ حفظ الملف كـ "تحديث جديد"
        ProjectAttachment.objects.create(
            project=project,
            file=file,
            file_name=file_name,
            description=description,
            uploaded_by=request.user,
            is_main_file=False  # ✅ يتم اعتباره تحديثًا وليس ملفًا رئيسيًا
        )

        messages.success(request, "File uploaded successfully as an update!")
        return redirect('project_detail', project_id=project.id)

    return render(request, 'project_detail.html', {
        'project': project,
        'members': members,
        'is_owner': is_owner,
        'is_member': is_member,
        'pending_requests': pending_requests,
        'user_join_request': user_join_request,
        'available_users': available_users,  # ✅ تمرير المستخدمين المتاحين لدعوتهم
        'main_files': main_files,  # ✅ تمرير الملفات الرئيسية إلى القالب
        'update_files': update_files,  # ✅ تمرير التحديثات إلى القالب
    })

@login_required
def delete_attachment(request, file_id):
    file = get_object_or_404(ProjectAttachment, id=file_id)

    # ✅ السماح فقط لمالك المشروع أو الشخص الذي رفع الملف بحذفه
    if request.user == file.uploaded_by or request.user == file.project.owner:
        file.delete()
        messages.success(request, "File deleted successfully!")
    else:
        messages.error(request, "You do not have permission to delete this file.")

    return redirect('project_detail', project_id=file.project.id)

@login_required
def create_project(request):
    if request.method == 'POST':
        print("✅ Received POST request!")  # 🔹 تحقق مما إذا كان الطلب يصل
        form = ProjectForm(request.POST, request.FILES)
        
        if form.is_valid():
            print("✅ Form is valid!")  # 🔹 تحقق مما إذا كان الفورم صالحًا
            
            project = form.save(commit=False)
            project.owner = request.user  
            
            # ✅ التحقق مما إذا كان `logo` صالحًا قبل الحفظ
            logo = request.FILES.get("logo")
            if logo:
                try:
                    project.logo = logo
                except Exception as e:
                    print(f"⚠️ Error saving logo: {e}")
                    messages.warning(request, "The logo file is not valid, but the project was created.")
            
            project.save()
            form.save_m2m()

            # ✅ حفظ الملفات كمرفقات رئيسية إذا تم رفعها
            for file in request.FILES.getlist('attachments'):
                attachment = ProjectAttachment.objects.create(
                    project=project,
                    file=file,
                    uploaded_by=request.user,
                    is_main_file=True
                )
                print(f"✅ Saved file: {attachment.file_name}, is_main_file: {attachment.is_main_file}")

            project.update_progress()
            messages.success(request, "Project created successfully!")
            print("✅ Redirecting to projects_list")
            return redirect('project_detail', project_id=project.id)
        
        else:
            print("❌ Form is not valid!", form.errors)  # 🔹 طباعة الأخطاء في الفورم
    
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
               ProjectAttachment.objects.create(project=project, file=file, uploaded_by=request.user)


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
CustomUser = get_user_model()

@login_required
def invite_members(request):
    """
    البحث الفوري عن المستخدمين وإرسال دعوات بعد اختيار المستخدمين والمشروع،
    مع حفظ التحديدات في الجلسة لضمان بقائها بعد البحث.
    """

    # ✅ جلب المشاريع التي يملكها المستخدم
    user_projects = Project.objects.filter(owner=request.user)

    # ✅ جلب التحديدات المحفوظة من الجلسة
    selected_users = request.session.get("selected_users", [])

    search_query = request.GET.get("search_query", "").strip()
    available_users = []

    # ✅ البحث الفوري في قاعدة البيانات عند إدخال أي قيمة
    if search_query:
        available_users = CustomUser.objects.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        ).exclude(id=request.user.id)

    # ✅ معالجة إضافة التحديدات إلى الجلسة
    if request.method == "POST":
        project_id = request.POST.get("project_id")
        selected_users = request.POST.getlist("selected_users")

        # ✅ طباعة القيم المستلمة للتأكد أنها تصل بشكل صحيح
        print("📩 Received POST Data:", request.POST)
        print("✅ Selected Users:", selected_users)

        # ✅ حفظ التحديدات في الجلسة لضمان بقائها بعد البحث
        request.session["selected_users"] = selected_users
        request.session.modified = True  # تحديث الجلسة

        if request.method == "POST":
            if not project_id or not selected_users:
                messages.error(request, "Please select a project and at least one user.")
                return redirect("invite_members")

            project = get_object_or_404(Project, id=project_id, owner=request.user)

            for user_id in selected_users:
                user = get_object_or_404(CustomUser, id=user_id)

                # ✅ التأكد مما إذا كان المستخدم عضوًا بالفعل في المشروع
                if project.members.filter(id=user.id).exists():
                    messages.warning(request, f"{user.username} هو بالفعل عضو في المشروع.")
                    continue

                existing_invitation = ProjectInvitation.objects.filter(project=project, invited_user=user).first()

                if existing_invitation:
                    if existing_invitation.status in ['canceled', 'rejected']:
                        # ✅ تحديث الدعوة القديمة وإعادة إرسالها بحالة `pending`
                        existing_invitation.status = 'pending'
                        existing_invitation.save()
                        messages.info(request, f"🔄 تمت إعادة إرسال الدعوة إلى {user.username}.")
                    else:
                        messages.info(request, f"🔄 {user.username} لديه دعوة سارية بالفعل.")
                        continue
                else:
                    # ✅ إرسال دعوة جديدة إذا لم تكن موجودة
                    ProjectInvitation.objects.create(
                        project=project,
                        invited_user=user,
                        status='pending'
                    )
                    messages.success(request, f"✅ تمت دعوة {user.username} بنجاح.")

            # ✅ تفريغ الجلسة بعد الإرسال
            request.session["selected_users"] = []
            request.session.modified = True

            # ✅ طباعة جميع الدعوات المخزنة للتحقق
            print("📜 All Invitations in Database:", ProjectInvitation.objects.all())

            return redirect("invite_members")

    return render(request, "invite_members.html", {
        "user_projects": user_projects,
        "available_users": available_users,
        "search_query": search_query,
        "selected_users": selected_users,  # ✅ تمرير التحديدات للقالب
    })


# 📌 إرسال طلب انضمام إلى مشروع
@login_required
def send_join_request(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # ✅ التحقق مما إذا كان المستخدم قد أرسل طلبًا بالفعل
    if JoinRequest.objects.filter(project=project, user=request.user).exists():
        messages.info(request, "You have already sent a request to join this project.")
    else:
        # ✅ التأكد من حفظ الطلب بحالة "Pending"
        join_request = JoinRequest.objects.create(project=project, user=request.user, status='pending')
        join_request.save()  # ✅ حفظ الطلب بشكل صحيح

        # ✅ طباعة بيانات الطلب في `Terminal` للتحقق
        print(f"✅ New Join Request Created -> User: {join_request.user.username}, Project: {join_request.project.name}, Status: {join_request.status}")

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

    # ✅ التحقق مما إذا كانت الدعوة قد تم الرد عليها مسبقًا
    if invitation.status != 'pending':
        messages.warning(request, "This invitation has already been processed.")
        return redirect('received_invitations')

    if response == 'accept':
        invitation.status = 'accepted'
        invitation.project.members.add(request.user)
        invitation.save()
        messages.success(request, f"You have successfully joined the project: {invitation.project.name}!")
    
    elif response == 'reject':
        invitation.status = 'rejected'
        invitation.save()
        messages.info(request, "You have declined the invitation.")
    
    else:
        messages.error(request, "Invalid response.")
        return redirect('received_invitations')

    return redirect('received_invitations')  # ✅ إعادة التوجيه إلى صفحة الدعوات المستلمة

@login_required
def received_invitations(request):
    # ✅ جلب الدعوات التي استلمها المستخدم
    invitations = ProjectInvitation.objects.filter(invited_user=request.user).select_related('project')


    sent_requests = ProjectInvitation.objects.filter(project__owner=request.user).select_related('invited_user', 'project')

    # ✅ جلب الطلبات التي تلقاها المستخدم كمشرف للمشروع
    received_requests = JoinRequest.objects.filter(project__owner=request.user)

    # ✅ طباعة البيانات للتحقق في الكونسول
    print("Invitations:", invitations)
    print("Sent Requests:", sent_requests)  # ✅ تحقق من أن الطلبات المرسلة يتم جلبها الآن
    print("Received Requests:", received_requests)

    return render(request, 'received_invitations.html', {
        'invitations': invitations,
        'sent_requests': sent_requests,  # ✅ تمرير جميع الطلبات المرسلة
        'received_requests': received_requests  # ✅ تمرير جميع الطلبات المستلمة
    })

@login_required
def cancel_join_request(request, request_id):
    print(f"🚀 Attempting to cancel invitation with ID: {request_id}")

    # ✅ البحث عن الدعوة في `ProjectInvitation`
    invitation = get_object_or_404(ProjectInvitation, id=request_id, project__owner=request.user, status='pending')

    print(f"🔍 Found ProjectInvitation -> ID: {invitation.id}, Status: {invitation.status}")

    # ✅ تحديث حالة الدعوة إلى "canceled"
    invitation.status = 'canceled'
    invitation.save()

    # ✅ تحديث `JoinRequest` بحيث لا يستطيع المستخدم المدعو قبوله بعد الإلغاء
    join_request = JoinRequest.objects.filter(
        project=invitation.project, user=invitation.invited_user, status='pending'
    ).first()

    if join_request:
        print(f"🔄 Found JoinRequest -> ID: {join_request.id}, Status: {join_request.status}")
        join_request.status = 'canceled'
        join_request.save()
        print(f"✅ JoinRequest {join_request.id} successfully canceled!")
    else:
        print("⚠ No matching JoinRequest found for this invitation.")

    print(f"✅ Invitation {request_id} successfully canceled!")
    messages.success(request, "The invitation has been canceled successfully.")

    # ✅ إعادة المستخدم إلى نفس الصفحة بدلاً من إعادة التوجيه إلى قائمة الطلبات
    return redirect(request.META.get('HTTP_REFERER', 'project_requests'))

@login_required
def remove_member(request, project_id, user_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    user = get_object_or_404(CustomUser, id=user_id)
    project.members.remove(user)
    messages.success(request, f"{user.username} has been removed from the project.")
    return redirect('project_requests') 


@login_required
def dashboard(request):
    projects_count = Project.objects.filter(owner=request.user).count()
    completed_tasks_count = 10  # يجب استبداله ببيانات حقيقية من قاعدة البيانات
    pending_tasks_count = 5  # يجب استبداله ببيانات حقيقية من قاعدة البيانات
    user_rating = 4.5  # مثال، يجب استبداله بتقييم المستخدم الحقيقي

    # ✅ جلب الطلبات الصادرة والواردة
    sent_requests_count = JoinRequest.objects.filter(user=request.user).count()
    received_requests_count = JoinRequest.objects.filter(project__owner=request.user, status='pending').count()

    return render(request, 'dashboard.html', {
        'projects_count': projects_count,
        'completed_tasks_count': completed_tasks_count,
        'pending_tasks_count': pending_tasks_count,
        'user_rating': user_rating,
        'sent_requests_count': sent_requests_count,  # ✅ تمرير الطلبات الصادرة
        'received_requests_count': received_requests_count,  # ✅ تمرير الطلبات الواردة
    })
