from django.urls import path
from . import views

urlpatterns = [
    path('', views.diagram_list, name='diagrams_list'),
    path('<int:diagram_id>/', views.diagram_detail, name='diagram_detail'),
]
