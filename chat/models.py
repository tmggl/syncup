from django.db import models
from users.models import CustomUser
from projects.models import Project
from django.core.validators import MinValueValidator, MaxValueValidator

class ChatRoom(models.Model):
    """
    نموذج يمثل غرفة دردشة.
    يمكن أن تكون الغرفة:
    - مرتبطة بمشروع (Project Chat)
    - بين مستخدمين فقط (Private Chat)
    - عامة (Public Chat)
    - بين مستخدم وخبير (Expert Chat)
    """
    ROOM_TYPES = [
        ('project', 'Project Chat'),
        ('private', 'Private Chat'),
        ('public', 'Public Chat'),
        ('expert', 'Expert Chat'),
    ]

    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    name = models.CharField(max_length=255, blank=True, null=True)  # اسم وصفي اختياري
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    participants = models.ManyToManyField(CustomUser, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.room_type == 'project' and self.project:
            return f"Project Chat: {self.project.name}"
        elif self.room_type == 'expert':
            return f"Expert Chat: {self.name or 'Unnamed'}"
        elif self.room_type == 'private':
            return f"Private Chat: {self.name or 'Unnamed'}"
        elif self.room_type == 'public':
            return "Public Site Chat"
        return f"Chat Room ({self.room_type})"


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField(blank=True)
    attachment = models.FileField(upload_to='chat_attachments/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    is_deleted = models.BooleanField(default=False)  # 
    is_read = models.BooleanField(default=False)     #  (لتمييز الرسائل المقروءة من غيرها)

    def __str__(self):
        return f"{self.sender.username} → Room {self.room.id} | {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    def is_image(self):
        return self.attachment and self.attachment.url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))

    def is_audio(self):
        return self.attachment and self.attachment.url.lower().endswith(('.mp3', '.wav', '.ogg'))

    def is_file(self):
        return self.attachment and not self.is_image() and not self.is_audio()


class ExpertRating(models.Model):
    expert = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='ratings',
        limit_choices_to={'role': 'expert'}
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='given_ratings'
    )
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['expert', 'user']  # لا يمكن لمستخدم تقييم نفس الخبير أكثر من مرة

    def __str__(self):
        return f"{self.user} rated {self.expert} - {self.rating}"
