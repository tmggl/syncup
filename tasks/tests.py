from django.db import models
from users.models import CustomUser
from projects.models import Project

# نموذج المهمة، يحتوي على بيانات المهمة وعلاقتها بالمشروع والمستخدم المسؤول عنها
class Task(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('urgent', 'Urgent'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=255)  # عنوان المهمة
    description = models.TextField(blank=True, null=True)  # وصف المهمة
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')  # حالة المهمة
    project = models.ForeignKey(Project, on_delete=models.CASCADE)  # المهمة مرتبطة بمشروع معين
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)  # الشخص المسؤول عن المهمة
    due_date = models.DateField(blank=True, null=True)  # تاريخ التسليم
    created_at = models.DateTimeField(auto_now_add=True)  # وقت إنشاء المهمة

    def __str__(self):
        return self.title
