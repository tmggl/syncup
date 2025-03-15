from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Meeting, ExpertAvailability
from users.models import CustomUser
from .forms import MeetingForm
import uuid

# ✅ عرض جميع الاجتماعات التي يمكن للمستخدم حضورها
@login_required
def meeting_list(request):
    meetings = Meeting.objects.filter(participants=request.user) | Meeting.objects.filter(expert=request.user)
    return render(request, 'meetings_list.html', {'meetings': meetings})  


# ✅ عرض تفاصيل اجتماع معين
@login_required
def meeting_detail(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    if request.user not in meeting.participants.all() and request.user != meeting.expert:
        messages.error(request, "You are not authorized to view this meeting.")
        return redirect('meeting_list')
    
    return render(request, 'meeting_detail.html', {'meeting': meeting})

# ✅ إنشاء اجتماع جديد يدويًا (للمستخدمين العاديين فقط)
@login_required
def create_meeting(request):
    if request.user.role != 'member':  # ✅ فقط الأعضاء يمكنهم إنشاء الاجتماعات
        messages.warning(request, "Only members can create meetings.")
        return redirect('meeting_list')
    
    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.save()
            form.save_m2m()
            messages.success(request, "Meeting created successfully.")
            return redirect('meeting_list')
    else:
        form = MeetingForm()
    
    return render(request, 'create_meeting.html', {'form': form})

# ✅ طلب اجتماع مع خبير بناءً على المواعيد المتاحة
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
        
        slot.is_booked = True  # ✅ تحديد الموعد كمحجوز
        slot.save()

        messages.success(request, f"Meeting with {expert.username} scheduled successfully.")
        return redirect('meeting_list')
    
    return render(request, 'request_expert_meeting.html', {'experts': experts, 'available_slots': available_slots})

# ✅ تعديل اجتماع (فقط للمضيف أو المشاركين)
@login_required
def edit_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    if request.user != meeting.expert and request.user not in meeting.participants.all():
        messages.error(request, "You are not authorized to edit this meeting.")
        return redirect('meeting_list')
    
    if request.method == 'POST':
        form = MeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            form.save()
            messages.success(request, "Meeting updated successfully.")
            return redirect('meeting_detail', meeting_id=meeting.id)
    else:
        form = MeetingForm(instance=meeting)
    
    return render(request, 'edit_meeting.html', {'form': form, 'meeting': meeting})

# ✅ حذف اجتماع (فقط للخبير أو المشاركين)
@login_required
def delete_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    if request.user != meeting.expert and request.user not in meeting.participants.all():
        messages.error(request, "You are not authorized to delete this meeting.")
        return redirect('meeting_list')
    
    meeting.delete()
    messages.success(request, "Meeting deleted successfully.")
    return redirect('meeting_list')

# ✅ الموافقة على اجتماع خبير وإنشاء رابط الاجتماع تلقائيًا
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
