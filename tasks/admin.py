from django.contrib import admin
from .models import Task  # ✅ تأكد من أن الاستيراد صحيح

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'assigned_to', 'status', 'due_date', 'created_at')  # ✅ عرض الحقول الرئيسية
    list_filter = ('status', 'project')  # ✅ تصفية حسب الحالة والمشروع
    search_fields = ('title', 'assigned_to__user__username')  # ✅ تأكد من أن `assigned_to` مرتبط بـ `CustomUser`
