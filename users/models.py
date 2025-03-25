from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    phone_regex = RegexValidator(
        regex=r'^05\d{8}$', 
        message="Phone number must start with 05 and be exactly 10 digits."
    )
    
    phone_number = models.CharField(
        max_length=10, 
        unique=True, 
        validators=[phone_regex],
        help_text="Phone number must start with 05 and contain exactly 10 digits."
    )

    ROLE_CHOICES = [
        ('member', 'Member'),
        ('expert', 'Expert')
    ]

    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='member'
    )

    profile_image = models.ImageField(
        upload_to='profile_pics/', 
        default='profile_pics/p.png',
        blank=True,
        null=True
    )

    # Bio fields: short and full
    short_bio = models.CharField(
        max_length=15,
        blank=True,
        help_text="Short description (e.g., AI Expert, UI Guru)."
    )

    full_bio = models.TextField(
        blank=True,
        help_text="Detailed biography or personal summary."
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
