from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Meeting, ExpertAvailability
from users.models import CustomUser
from projects.models import Project
from .forms import ManualMeetingForm
from django.utils import timezone
from django.db.models import Q
from django.db.models import Avg
from chat.models import ExpertRating

# ✅ List all meetings related to the user

@login_required
def meeting_list(request):
    meetings = Meeting.objects.filter(
        Q(participants=request.user) | Q(expert=request.user)
    ).order_by('-date', '-time')  # ترتيب من الأحدث إلى الأقدم

    today = timezone.localdate()  # نحتفظ به لاستخدامه في القالب

    return render(request, 'meetings_list.html', {
        'meetings': meetings,
        'today': today  # نمرره للقالب
    })

# ✅ Show meeting details
@login_required
def meeting_detail(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    if request.user not in meeting.participants.all() and request.user != meeting.expert:
        messages.error(request, "You are not authorized to view this meeting.")
        return redirect('meeting_list')

    return render(request, 'meeting_detail.html', {'meeting': meeting})


#  Create a new meeting linked to a project and auto-assign team members
@login_required
def create_meeting(request):
    if request.user.role != 'member':
        messages.warning(request, "Only members are allowed to create meetings.")
        return redirect('meeting_list')

    # ✅ الحصول على المشروع من GET
    project_id = request.GET.get('project')
    project = get_object_or_404(Project, id=project_id) if project_id else None

    # ✅ أعضاء الفريق حسب المشروع
    team_members = []
    if project:
        team_members = project.members.all()

    # ✅ تحديد المشاركين المحددين مسبقًا (لإعادة إظهار الاختيار عند إعادة تحميل)
    selected_participants = request.POST.getlist('participants') if request.method == 'POST' else []

    if request.method == 'POST':
        form = ManualMeetingForm(request.POST, user=request.user)
        if form.is_valid():
            meeting = form.save(commit=False)

            # ✅ تعيين المشروع إذا لم يكن محددًا من الفورم
            if not meeting.project:
                meeting.project = project

            # ✅ تعيين من أنشأ الاجتماع
            meeting.created_by = request.user

            meeting.save()

            # ✅ تعيين المشاركين (بما فيهم المالك، أُضيف من الفورم تلقائيًا)
            participants = form.cleaned_data['participants']
            meeting.participants.set(participants)

            form.save_m2m()

            messages.success(request, "Meeting created successfully.")
            return redirect('meeting_list')
    else:
        form = ManualMeetingForm(request.GET or None, initial={'project': project}, user=request.user)

    return render(request, 'create_meeting.html', {
        'form': form,
        'project': project,
        'team_members': team_members,
        'selected_participants': selected_participants,  # ✅ التمرير للقالب
    })

# ✅ Edit a meeting (only expert or participants allowed)
@login_required
def edit_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    if request.user != meeting.expert and request.user not in meeting.participants.all():
        messages.error(request, "You are not authorized to edit this meeting.")
        return redirect('meeting_list')

    if request.method == 'POST':
        form = ManualMeetingForm(request.POST, instance=meeting, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Meeting updated successfully.")
            return redirect('meeting_detail', meeting_id=meeting.id)
    else:
        form = ManualMeetingForm(instance=meeting, user=request.user)

    return render(request, 'edit_meeting.html', {'form': form, 'meeting': meeting})


# ✅ Delete a meeting (only expert or participants allowed)
@login_required
def delete_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    if request.user != meeting.expert and request.user not in meeting.participants.all():
        messages.error(request, "You are not authorized to delete this meeting.")
        return redirect('meeting_list')

    meeting.delete()
    messages.success(request, "Meeting deleted successfully.")
    return redirect('meeting_list')


# ✅ Approve expert meeting and generate meeting link
@login_required
def approve_expert_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)

    # فقط الخبير يستطيع الموافقة
    if request.user != meeting.expert:
        messages.error(request, "You are not authorized to approve this meeting.")
        return redirect('meeting_list')

    if request.method == 'POST':
        meeting_link = request.POST.get('meeting_link')
        platform = request.POST.get('platform', 'zoom')

        meeting.meeting_link = meeting_link
        meeting.platform = platform
        meeting.status = 'approved'
        meeting.save()

        messages.success(request, "Meeting approved and link saved.")
        return redirect('meeting_detail', meeting_id=meeting.id)

    return render(request, 'approve_meeting.html', {'meeting': meeting})


# ✅ Request a meeting with an expert from available slots

@login_required
def request_expert_meeting(request):
    expert_id = request.GET.get('expert_id')
    experts = CustomUser.objects.filter(role='expert')
    all_slots = ExpertAvailability.objects.all()

    if expert_id:
        expert = get_object_or_404(CustomUser, id=expert_id, role='expert')
        experts = [expert]
        all_slots = all_slots.filter(expert=expert).order_by('date', 'start_time')

        # ✅ حساب عدد الاجتماعات لهذا الخبير
        session_count = Meeting.objects.filter(expert=expert).count()
        expert.session_count = session_count  # مؤقت للعرض في القالب فقط
    else:
        expert = None
        all_slots = all_slots.order_by('date', 'start_time')

    if request.method == 'POST':
        slot_id = request.POST.get('slot')
        subject = request.POST.get('subject')

        slot = get_object_or_404(ExpertAvailability, id=slot_id, is_booked=False)
        expert = slot.expert

        # ✅ إنشاء الاجتماع مع ربط الموعد availability بالاجتماع
        meeting = Meeting.objects.create(
            title=subject,
            date=slot.date,
            time=slot.start_time,
            expert=expert,
            status='pending',
            created_by=request.user,
            availability=slot  # ✅ الربط المهم هنا
        )
        meeting.participants.add(request.user)
        meeting.save()

        # ✅ تأشير الموعد على أنه تم حجزه
        slot.is_booked = True
        slot.save()

        messages.success(request, f"Your request to meet with {expert.get_full_name() or expert.username} has been submitted. Awaiting approval.")
        return redirect('meeting_list')

    return render(request, 'request_expert_meeting.html', {
        'experts': experts,
        'available_slots': all_slots,
        'selected_expert': expert
    })


@login_required
def expert_availability_manage(request):
    if request.user.role != 'expert':
        return redirect('meeting_list')

    if request.method == 'POST':
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')

        ExpertAvailability.objects.create(
            expert=request.user,
            date=date,
            start_time=start_time,
            is_booked=False
        )
        messages.success(request, "Time slot added successfully.")
        return redirect('expert_availability_manage')

    # ✅ جلب المواعيد الخاصة بالخبير
    slots = ExpertAvailability.objects.filter(
        expert=request.user
    ).order_by('date', 'start_time')

    # ✅ حساب عدد الجلسات والتقييم
    session_count = Meeting.objects.filter(expert=request.user).count()
    avg_rating = ExpertRating.objects.filter(expert=request.user).aggregate(avg=Avg('rating'))['avg'] or 0.0


    expert = request.user
    expert.session_count = session_count
    expert.avg_rating = round(avg_rating, 1)

    return render(request, 'expert_availability_manage.html', {
        'slots': slots,
        'expert': expert,  # 🟢 هنا نمرر المتغير للقالب
    })

@login_required
def delete_availability_slot(request, slot_id):
    slot = get_object_or_404(ExpertAvailability, id=slot_id, expert=request.user)
    if slot.is_booked:
        messages.error(request, "You can't delete a booked slot.")
    else:
        slot.delete()
        messages.success(request, "Slot deleted successfully.")
    return redirect('expert_availability_manage')

@login_required
def edit_availability_slot(request, slot_id):
    slot = get_object_or_404(ExpertAvailability, id=slot_id, expert=request.user)

    if slot.is_booked:
        messages.error(request, "You can't edit a booked slot.")
        return redirect('expert_availability_manage')

    if request.method == 'POST':
        slot.date = request.POST.get('date')
        slot.start_time = request.POST.get('start_time')
        slot.end_time = request.POST.get('end_time') or None
        slot.save()
        messages.success(request, "Slot updated successfully.")
        return redirect('expert_availability_manage')

    return render(request, 'edit_availability_slot.html', {'slot': slot})

@login_required
def reject_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    if request.user != meeting.expert:
        messages.error(request, "You are not authorized to reject this meeting.")
        return redirect('meeting_list')

    meeting.status = 'rejected'
    meeting.save()
    messages.success(request, "Meeting rejected.")
    return redirect('expert_availability_manage')
