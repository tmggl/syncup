from django.db import models
from users.models import CustomUser
from projects.models import Project

class Task(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),  # Task created but not yet assigned
        ('pending', 'Pending'),  # Awaiting user approval
        ('in_progress', 'In Progress'),  # Accepted and being worked on
        ('urgent', 'Urgent'),  # Marked as urgent
        ('completed', 'Completed'),  # Task completed
        ('rejected', 'Rejected'),  # User declined the task
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')  # ✅ Link task to a project
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')  # ✅ Assign task to a user
    due_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    files = models.FileField(upload_to='task_attachments/', blank=True, null=True)  # ✅ Support for file uploads

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        """✅ Update project progress automatically when a task is saved."""
        super().save(*args, **kwargs)
        if self.project:
            self.project.update_progress()  # ✅ Recalculate progress after saving a task
class TaskUpdate(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="updates")  # ✅ ربط التحديث بالمهمة
    file = models.FileField(upload_to="task_updates/")  # ✅ تخزين الملف المرفق
    description = models.TextField(blank=True, null=True)  # ✅ وصف التحديث
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # ✅ المستخدم الذي رفع التحديث
    uploaded_at = models.DateTimeField(auto_now_add=True)  # ✅ تاريخ الرفع

    def __str__(self):
        return f"Update for {self.task.title} by {self.uploaded_by.username}"
