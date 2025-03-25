from django.db import models
from projects.models import Project
from users.models import CustomUser

class Meeting(models.Model):
    PLATFORM_CHOICES = [
        ('zoom', 'Zoom'),
        ('meet', 'Google Meet'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),        # تم طلب الاجتماع وينتظر موافقة الخبير
        ('approved', 'Approved'),      # تمت الموافقة من قبل الخبير
        ('rejected', 'Rejected'),      # تم رفض الطلب من الخبير
        ('cancelled', 'Cancelled'),    # تم إلغاء الاجتماع بعد الموافقة
    ]

    title = models.CharField(max_length=255)  # عنوان الاجتماع
    description = models.TextField(blank=True, null=True)  # تفاصيل الاجتماع
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, blank=True, related_name="meeting_set"
    )
    date = models.DateField()
    time = models.TimeField()
    participants = models.ManyToManyField(CustomUser, related_name="meetings")
    expert = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expert_meetings",
        limit_choices_to={'role': 'expert'}
    )
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='meetings_created'
    )
    availability = models.OneToOneField(  # ✅ الربط المباشر بالموعد
        'meetings.ExpertAvailability',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='meeting'
    )
    meeting_link = models.CharField(max_length=255, blank=True, null=True)
    platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES, default='zoom')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

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
    end_time = models.TimeField(null=True, blank=True)  # ✅ الآن اختياري
    is_booked = models.BooleanField(default=False)  # حالة الحجز

    def __str__(self):
        return f"{self.expert.username} - {self.date} ({self.start_time} - {self.end_time or 'N/A'})"

