from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from users.views import home_view  # تأكد من استيراد `home_view`

urlpatterns = [
    path('admin/', admin.site.urls),  # لوحة تحكم Django
    path('', home_view, name='home'),  # الصفحة الرئيسية
    path('users/', include('users.urls')),  # روابط المستخدمين
    path('projects/', include('projects.urls')),  # روابط المشاريع
    path('tasks/', include('tasks.urls')),  # روابط المهام
    path('meetings/', include('meetings.urls')),  # روابط الاجتماعات
    path('diagrams/', include('diagrams.urls')),  # روابط المخططات
    path('chat/', include('chat.urls')),  # روابط الدردشة
]

# 📂 تقديم ملفات media و static في بيئة التطوير أو الإنتاج
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]
