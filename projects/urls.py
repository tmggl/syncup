from django.urls import path
from .views import dashboard
from .views import invite_members
from .views import cancel_join_request
from .views import delete_attachment
from .views import (
    project_list, project_detail, create_project, update_project, delete_project,
     respond_to_invitation, send_join_request, respond_to_join_request,
    project_requests, received_invitations  # ✅ إضافة `received_invitations`
)

urlpatterns = [
    path('', project_list, name='projects_list'),  # عرض جميع المشاريع
    path('<int:project_id>/', project_detail, name='project_detail'),  # عرض تفاصيل مشروع معين
    path('create/', create_project, name='create_project'),  # إضافة مشروع جديد
    path('<int:project_id>/edit/', update_project, name='update_project'),  # تعديل مشروع
    path('<int:project_id>/delete/', delete_project, name='delete_project'),  # حذف مشروع
    path('dashboard/', dashboard, name='dashboard'),


    # إدارة الدعوات
    path('invite-members/', invite_members, name='invite_members'),  
    path('invitation/<int:invitation_id>/<str:response>/', respond_to_invitation, name='respond_to_invitation'),  # قبول/رفض دعوة
    path('invitations/', received_invitations, name='received_invitations'),  # ✅ عرض الدعوات المستلمة

    # إدارة طلبات الانضمام
    path('<int:project_id>/join/', send_join_request, name='send_join_request'),  # إرسال طلب انضمام
    path('requests/', project_requests, name='project_requests'),  # ✅ تصحيح اسم العرض ليطابق `views.py`
    path('join-request/<int:request_id>/<str:response>/', respond_to_join_request, name='respond_to_join_request'),  
    path('join-request/cancel/<int:request_id>/', cancel_join_request, name='cancel_join_request'),
    path('delete-attachment/<int:file_id>/', delete_attachment, name='delete_attachment'),   

]
