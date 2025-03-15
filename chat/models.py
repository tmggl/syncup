from django.db import models
from users.models import CustomUser

# ✅ نموذج المحادثة بين المستخدم والخبراء
class Chat(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='user_chats'
    )  # المستخدم
    expert = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='expert_chats', limit_choices_to={'role': 'expert'}
    )  # الخبير فقط
    created_at = models.DateTimeField(auto_now_add=True)  # وقت بدء المحادثة

    def __str__(self):
        return f"Chat between {self.user.username} and {self.expert.username}"

# ✅ نموذج الرسائل داخل المحادثة
class Message(models.Model):
    chat = models.ForeignKey(
        Chat, on_delete=models.CASCADE, related_name='messages'
    )  # المحادثة المرتبطة بهذه الرسالة
    sender = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='sent_messages'
    )  # المرسل
    content = models.TextField()  # محتوى الرسالة
    timestamp = models.DateTimeField(auto_now_add=True)  # وقت الإرسال

    def __str__(self):
        return f"Message from {self.sender.username} in Chat {self.chat.id}"
