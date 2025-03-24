from django.db import models
from projects.models import Project
from users.models import CustomUser
import uuid

class Meeting(models.Model):
    PLATFORM_CHOICES = [
        ('zoom', 'Zoom'),
        ('meet', 'Google Meet'),
    ]

    title = models.CharField(max_length=255)  # عنوان الاجتماع
    description = models.TextField(blank=True, null=True)  # تفاصيل الاجتماع
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, blank=True, related_name="meeting_set"
    )  # الاجتماع مرتبط بمشروع معين (اختياري)
    date = models.DateField()  # تاريخ الاجتماع
    time = models.TimeField()  # وقت الاجتماع
    participants = models.ManyToManyField(CustomUser, related_name="meetings")  # المشاركون في الاجتماع
    expert = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expert_meetings",
        limit_choices_to={'role': 'expert'}  # يسمح فقط للخبراء
    )  # الخبير في الاجتماع
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='meetings_created'
    )  # الشخص الذي أنشأ الاجتماع
    meeting_link = models.CharField(max_length=255, blank=True, null=True)  # رابط الاجتماع
    platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES, default='zoom')  # نوع النظام المستخدم
    created_at = models.DateTimeField(auto_now_add=True)  # وقت الإنشاء

    def save(self, *args, **kwargs):
        """ إنشاء رابط الاجتماع تلقائيًا إذا كان الاجتماع يتضمن خبيرًا ولم يتم تعيين رابط مسبقًا """
        if self.expert and not self.meeting_link:
            self.meeting_link = f"https://meet.example.com/{uuid.uuid4()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.date} {self.time}"


class ExpertAvailability(models.Model):
    expert = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="availabilities",
        limit_choices_to={'role': 'expert'}  # يسمح فقط للخبراء
    )
    date = models.DateField()  # تاريخ التوفر
    start_time = models.TimeField()  # وقت بدء التوفر
    end_time = models.TimeField()  # وقت انتهاء التوفر
    is_booked = models.BooleanField(default=False)  # حالة الحجز

    def __str__(self):
        return f"{self.expert.username} - {self.date} ({self.start_time} - {self.end_time})"
