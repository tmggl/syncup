from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    phone_regex = RegexValidator(
        regex=r'^05\d{8}$', 
        message="رقم الجوال يجب أن يبدأ بـ 05 ويحتوي على 10 أرقام فقط."
    )
    
    phone_number = models.CharField(
        max_length=10, 
        unique=True, 
        validators=[phone_regex],
        help_text="رقم الجوال يجب أن يبدأ بـ 05 ويكون مكونًا من 10 أرقام."
    )

    ROLE_CHOICES = [
        ('member', 'Member'),  # العضو العادي
        ('expert', 'Expert')   # الخبير
    ]

    role = models.CharField(
    max_length=10, 
    choices=ROLE_CHOICES, 
    default='member'
    )

    #  أضف السطر هنا بعد role
    profile_image = models.ImageField(
    upload_to='profile_pics/', 
    default='profile_pics/p.png',  # تعيين صورة افتراضية عند إنشاء الحساب
    blank=True,
    null=True
    )

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True
    )

    def __str__(self):
        return f"{self.username} - {self.phone_number} ({self.get_role_display()})"
