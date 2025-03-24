from django.urls import path
from . import views
from .views import (
    chat_list,
    chat_detail,
    expert_page,
    chat_with_expert,
    chat_with_user,
    project_chat,
    public_chat,
)

urlpatterns = [
    # ✅ عرض جميع المحادثات التي يشارك فيها المستخدم
    path('', chat_list, name='chat_list'),

    # ✅ عرض تفاصيل محادثة معينة
    path('<int:room_id>/', chat_detail, name='chat_detail'),

    # ✅ صفحة الخبراء
    path('experts/', expert_page, name='expert_page'),

    # ✅ بدء محادثة مع خبير
    path('chat/expert/<int:expert_id>/', chat_with_expert, name='chat_with_expert'),

    # ✅ بدء محادثة خاصة مع مستخدم
    path('chat/user/<int:user_id>/', chat_with_user, name='chat_with_user'),

    # ✅ محادثة خاصة بمشروع
    path('chat/project/<int:project_id>/', project_chat, name='project_chat'),

    # ✅ المحادثة العامة للموقع
    path('chat/public/', public_chat, name='public_chat'),
    path('start/', views.start_private_chat, name='start_private_chat'),
    path('search-users/', views.search_users, name='search_users'),
    path('message/<int:message_id>/delete/', views.delete_message, name='delete_message'),

]
