from django.contrib import admin
from .models import ChatRoom, Message

# ✅ تخصيص عرض غرف الدردشة في Django Admin
@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'room_type', 'project', 'created_at')  # عرض اسم الغرفة، النوع، المشروع المرتبط، وتاريخ الإنشاء
    search_fields = ('name', 'project__title', 'participants__username')  # البحث بالاسم أو عنوان المشروع أو أسماء المشاركين
    list_filter = ('room_type', 'created_at')  # تصفية حسب نوع الغرفة وتاريخ الإنشاء
    filter_horizontal = ('participants',)  # واجهة سهلة لاختيار المشاركين

# ✅ تخصيص عرض الرسائل في Django Admin
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('room', 'sender', 'content', 'timestamp')  # عرض الرسائل مع معلوماتها الأساسية
    search_fields = ('sender__username', 'content')  # البحث في محتوى الرسائل
    list_filter = ('timestamp',)  # تصفية الرسائل حسب توقيت الإرسال
