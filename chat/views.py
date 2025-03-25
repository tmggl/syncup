from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ChatRoom
from .forms import MessageForm
from users.models import CustomUser
from projects.models import Project
from django.db.models import Q
from django.http import JsonResponse
from django.http import HttpResponseForbidden
from .models import Message
from django.db.models import Count
from .models import ExpertRating  


from django.db.models import Avg



# ✅ عرض جميع المحادثات التي يشارك بها المستخدم

@login_required
def chat_list(request):
    chats = ChatRoom.objects.filter(participants=request.user).annotate(
        unread_count=Count(
            'messages',
            filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user)
        )
    ).order_by('-created_at')
    return render(request, 'chat_list.html', {'chats': chats})


# ✅ عرض تفاصيل محادثة واحدة
@login_required
def chat_detail(request, room_id):
    chat = get_object_or_404(ChatRoom, id=room_id)

    # تأكد أن المستخدم من ضمن المشاركين
    if request.user not in chat.participants.all():
        return render(request, 'unauthorized.html', status=403)

    # ✅ تحديث الرسائل غير المقروءة إلى مقروءة (فقط إن لم تكن مرسلة من المستخدم)
    chat.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    # معالجة إرسال الرسالة
    form = MessageForm()
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.room = chat
            message.sender = request.user
            message.save()
            return redirect('chat_detail', room_id=chat.id)

    # جلب الرسائل بعد التحديث
    messages = chat.messages.all().order_by('timestamp')

    return render(request, 'chat_detail.html', {
        'chat': chat,
        'messages': messages,
        'form': form,
    })


# ✅ شات خاص بمشروع
@login_required
def project_chat(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    chat = ChatRoom.objects.filter(room_type='project', project=project).first()
    if not chat:
        chat = ChatRoom.objects.create(
            room_type='project',
            project=project,
            name=f"Project: {project.name}"
        )

    required_participants = set(project.members.all()) | {project.owner}
    if set(chat.participants.all()) != required_participants:
        chat.participants.set(required_participants)

    if request.user not in chat.participants.all():
        return render(request, 'unauthorized.html', status=403)

    return redirect('chat_detail', room_id=chat.id)


# ✅ شات عام
@login_required
def public_chat(request):
    chat = ChatRoom.objects.filter(room_type='public').first()
    if not chat:
        chat = ChatRoom.objects.create(room_type='public', name="Public Chat")
        chat.participants.set(CustomUser.objects.all())

    if request.user not in chat.participants.all():
        chat.participants.add(request.user)

    return redirect('chat_detail', room_id=chat.id)


# ✅ صفحة الخبراء


@login_required
def expert_page(request):
    experts = CustomUser.objects.filter(role='expert').exclude(id=request.user.id).annotate(
        avg_rating=Avg('ratings__rating'),
        rating_count=Count('ratings'),
        session_count=Count('chat_rooms', distinct=True)  # ✅ عدد المحادثات التي شارك فيها
    )
    return render(request, 'expert_page.html', {'experts': experts})


# ✅ محادثة مع خبير

@login_required
def chat_with_expert(request, expert_id):
    expert = get_object_or_404(CustomUser, id=expert_id, role='expert')

    chat = ChatRoom.objects.filter(
        Q(room_type='expert') &
        Q(participants=request.user) &
        Q(participants=expert)
    ).first()

    if not chat:
        chat = ChatRoom.objects.create(
            room_type='expert',
            name=f"{request.user.username} & {expert.username}"
        )
        chat.participants.set([request.user, expert])

    return redirect('chat_detail', room_id=chat.id)


# ✅ محادثة خاصة بين مستخدمين

@login_required
def chat_with_user(request, user_id):
    other_user = get_object_or_404(CustomUser, id=user_id)

    if other_user == request.user:
        return render(request, 'unauthorized.html', status=400)

    chat = ChatRoom.objects.filter(
        Q(room_type='private') &
        Q(participants=request.user) &
        Q(participants=other_user)
    ).first()

    if not chat:
        chat = ChatRoom.objects.create(
            room_type='private',
            name=f"{request.user.username} & {other_user.username}"
        )
        chat.participants.set([request.user, other_user])

    return redirect('chat_detail', room_id=chat.id)


@login_required
def start_private_chat(request):
    users = CustomUser.objects.exclude(id=request.user.id)

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if user_id:
            return redirect('chat_with_user', user_id=user_id)

    return render(request, 'start_private_chat.html', {
        'users': users
    })


@login_required
def search_users(request):
    query = request.GET.get("q", "")
    users = CustomUser.objects.exclude(id=request.user.id)

    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

    data = [{"id": u.id, "name": u.get_full_name() or u.username} for u in users[:10]]
    return JsonResponse(data, safe=False)


@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    # Only the sender of the message is allowed to delete it
    if message.sender != request.user:
        return HttpResponseForbidden("You are not allowed to delete this message.")

    # Soft-delete: clear the content and attachment, mark as deleted
    message.is_deleted = True
    message.content = ''
    message.attachment = None
    message.save()

    return redirect('chat_detail', room_id=message.room.id)


# ✅ عرض صفحة تقييم خبير
@login_required
def rate_expert(request, expert_id):
    expert = get_object_or_404(CustomUser, id=expert_id, role='expert')

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        ExpertRating.objects.update_or_create(
            user=request.user,
            expert=expert,
            defaults={'rating': rating, 'comment': comment}
        )
        return redirect('expert_page')

    return render(request, 'rate_expert.html', {'expert': expert})


# ✅ عرض جميع تقييمات المستخدمين لخبير معين
@login_required
def expert_reviews(request, expert_id):
    expert = get_object_or_404(CustomUser, id=expert_id, role='expert')
    ratings = ExpertRating.objects.filter(expert=expert).order_by('-created_at')

    # ✅ الرد على التقييم (مسموح فقط للخبير نفسه)
    if request.method == 'POST' and request.user == expert:
        rating_id = request.POST.get('rating_id')
        reply = request.POST.get('reply', '').strip()
        if rating_id and reply:
            rating = get_object_or_404(ExpertRating, id=rating_id, expert=expert)
            rating.reply = reply
            rating.save()
            return redirect('expert_reviews', expert_id=expert.id)

    return render(request, 'expert_reviews.html', {
        'expert': expert,
        'ratings': ratings,
    })
