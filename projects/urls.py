from django.urls import path
from .views import (
    project_list, project_detail, create_project, update_project, delete_project,
    send_invitation, respond_to_invitation, send_join_request, respond_to_join_request, project_requests
)

urlpatterns = [
    path('projects/', project_list, name='projects_list'),  # ✅ تأكد من أن هذا المسار صحيح
    path('projects/create/', create_project, name='create_project'),
    path('projects/<int:project_id>/', project_detail, name='project_detail'),
    path('projects/<int:project_id>/edit/', update_project, name='update_project'),
    path('projects/<int:project_id>/delete/', delete_project, name='delete_project'),

    # إدارة الدعوات
    path('projects/<int:project_id>/invite/<int:user_id>/', send_invitation, name='send_invitation'),
    path('projects/invitation/<int:invitation_id>/<str:response>/', respond_to_invitation, name='respond_to_invitation'),

    # إدارة طلبات الانضمام
    path('projects/<int:project_id>/join/', send_join_request, name='send_join_request'),
    path('projects/requests/', project_requests, name='project_requests'),
    path('projects/join-request/<int:request_id>/<str:response>/', respond_to_join_request, name='respond_to_join_request'),
]
