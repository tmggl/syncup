from django.urls import path
from .views import chat_list, chat_detail, expert_page, chat_with_expert  # ✅ الاستيرادات الصحيحة

urlpatterns = [
    path('', chat_list, name='chat_list'),  # ✅ عرض قائمة المحادثات
    path('<int:chat_id>/', chat_detail, name='chat_detail'),  # ✅ عرض تفاصيل المحادثة
    path('experts/', expert_page, name='expert_page'),  # ✅ عرض قائمة الخبراء
    path('chat/<int:expert_id>/', chat_with_expert, name='chat_with_expert'),  # ✅ بدء محادثة مع خبير
]
