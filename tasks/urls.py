from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_list, name='tasks_list'),
    path('<int:task_id>/', views.task_detail, name='task_detail'),
    path('<int:task_id>/update-status/', views.update_task_status, name='update_task_status'),  # ✅ إضافة رابط تحديث حالة المهمة
]