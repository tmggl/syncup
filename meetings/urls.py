from django.urls import path
from . import views

urlpatterns = [
    path('', views.meeting_list, name='meeting_list'),  # ✅ عرض قائمة الاجتماعات
    path('<int:meeting_id>/', views.meeting_detail, name='meeting_detail'),  # ✅ عرض تفاصيل اجتماع معين
    path('create/', views.create_meeting, name='create_meeting'),  # ✅ إنشاء اجتماع جديد
    path('request-expert/', views.request_expert_meeting, name='request_expert_meeting'),  # ✅ طلب اجتماع مع خبير
    path('<int:meeting_id>/edit/', views.edit_meeting, name='edit_meeting'),  # ✅ تعديل اجتماع
    path('<int:meeting_id>/delete/', views.delete_meeting, name='delete_meeting'),  # ✅ حذف اجتماع
    path('<int:meeting_id>/approve/', views.approve_expert_meeting, name='approve_expert_meeting'), 
    path('expert/availability/', views.expert_availability_manage, name='expert_availability_manage'),
    path('expert/availability/delete/<int:slot_id>/', views.delete_availability_slot, name='delete_availability_slot'),
    path('expert/availability/edit/<int:slot_id>/', views.edit_availability_slot, name='edit_availability_slot'),
    path('<int:meeting_id>/reject/', views.reject_meeting, name='reject_meeting'),

]
