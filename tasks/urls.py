from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_list, name='tasks_list'),  
    path('projects/<int:project_id>/tasks/', views.task_list, name='tasks_list_by_project'), 
    path('projects/<int:project_id>/tasks/create/', views.create_task, name='create_task'),
    path('<int:task_id>/', views.task_detail, name='task_detail'),
    path('sent/', views.sent_tasks, name='sent_tasks'),
    path('<int:task_id>/update-status/', views.update_task_status, name='update_task_status'),
    path('<int:task_id>/respond/<str:response>/', views.respond_to_task, name='respond_to_task'),
    path('<int:task_id>/upload-update/', views.upload_task_update, name='upload_task_update'),  
    path('<int:task_id>/progress/', views.task_progress, name='task_progress'),
]
