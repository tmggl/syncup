from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Chat, Message
from users.models import CustomUser  # ✅ استخدام `CustomUser` بدلاً من `Expert`

# ✅ عرض جميع المحادثات الخاصة بالمستخدم
@login_required
def chat_list(request):
    chats = Chat.objects.filter(user=request.user) | Chat.objects.filter(expert=request.user)
    return render(request, 'chat_list.html', {'chats': chats})  # ✅ تحميل القالب من `templates/`

# ✅ عرض تفاصيل محادثة معينة
@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    messages = Message.objects.filter(chat=chat)
    return render(request, 'chat_detail.html', {'chat': chat, 'messages': messages})  # ✅ تحميل القالب من `templates/`

# ✅ عرض قائمة الخبراء
@login_required
def expert_page(request):
    experts = CustomUser.objects.filter(role='expert')  # ✅ جلب جميع المستخدمين الذين لديهم `role='expert'`
    return render(request, 'expert_page.html', {'experts': experts})  # ✅ تحميل القالب من `templates/`

# ✅ بدء محادثة مع خبير معين
@login_required
def chat_with_expert(request, expert_id):
    expert = get_object_or_404(CustomUser, id=expert_id, role='expert')

    # ✅ التحقق مما إذا كان هناك محادثة قائمة بين المستخدم والخبير
    chat, created = Chat.objects.get_or_create(user=request.user, expert=expert)

    return render(request, 'chat_detail.html', {'chat': chat, 'expert': expert})  # ✅ تحميل القالب من `templates/`
