from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Meeting, ExpertAvailability
from users.models import CustomUser
from projects.models import Project
from .forms import ManualMeetingForm
import uuid
from django.utils import timezone
from django.db.models import Q
# ✅ List all meetings related to the user

@login_required
def meeting_list(request):
    today = timezone.localdate()

    # ✅ الاجتماعات التي يشارك فيها المستخدم أو هو الخبير
    meetings = Meeting.objects.filter(
        (Q(participants=request.user) | Q(expert=request.user)),
        date__gte=today
    ).order_by('date', 'time')

    return render(request, 'meetings_list.html', {'meetings': meetings})


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
    if request.user != meeting.expert:
        messages.error(request, "You are not authorized to approve this meeting.")
        return redirect('meeting_list')

    if not meeting.meeting_link:
        meeting.meeting_link = f"https://meet.example.com/{uuid.uuid4()}"
        meeting.save()
        messages.success(request, "Meeting link generated successfully.")

    return redirect('meeting_detail', meeting_id=meeting.id)


# ✅ Request a meeting with an expert from available slots
@login_required
def request_expert_meeting(request):
    experts = CustomUser.objects.filter(role='expert')
    available_slots = ExpertAvailability.objects.filter(is_booked=False)

    if request.method == 'POST':
        expert_id = request.POST.get('expert')
        slot_id = request.POST.get('slot')
        subject = request.POST.get('subject')

        expert = get_object_or_404(CustomUser, id=expert_id, role='expert')
        slot = get_object_or_404(ExpertAvailability, id=slot_id, expert=expert, is_booked=False)

        meeting = Meeting.objects.create(
            title=subject,
            date=slot.date,
            time=slot.start_time,
            expert=expert
        )
        meeting.participants.add(request.user)
        meeting.save()

        slot.is_booked = True
        slot.save()

        messages.success(request, f"Meeting with {expert.username} scheduled successfully.")
        return redirect('meeting_list')

    return render(request, 'request_expert_meeting.html', {
        'experts': experts,
        'available_slots': available_slots
    })
