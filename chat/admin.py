from django.contrib import admin
from .models import Chat, Message

# ✅ تخصيص عرض المحادثات في Django Admin
@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('user', 'expert', 'created_at')  # ✅ عرض المستخدم والخبير وتاريخ الإنشاء
    search_fields = ('user__username', 'expert__username')  # ✅ البحث في أسماء المستخدمين
    list_filter = ('created_at',)  # ✅ تصفية المحادثات حسب تاريخ الإنشاء

# ✅ تخصيص عرض الرسائل في Django Admin
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'sender', 'content', 'timestamp')  # ✅ عرض الرسائل مع معلوماتها الأساسية
    search_fields = ('sender__username', 'content')  # ✅ البحث في محتوى الرسائل
    list_filter = ('timestamp',)  # ✅ تصفية الرسائل حسب توقيت الإرسال
