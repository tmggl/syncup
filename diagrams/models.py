from django.db import models
from projects.models import Project
from users.models import CustomUser

# نموذج المخطط، يخزن المخططات التفاعلية كبيانات JSON
class Diagram(models.Model):
    name = models.CharField(max_length=255)  # اسم المخطط
    project = models.ForeignKey(Project, on_delete=models.CASCADE)  # المخطط مرتبط بمشروع معين
    data = models.JSONField()  # بيانات المخطط بصيغة JSON
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # الشخص الذي أنشأ المخطط
    created_at = models.DateTimeField(auto_now_add=True)  # وقت الإنشاء

    def __str__(self):
        return self.name
