from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    home_view, users_list, login_view, logout_view, register_view, dashboard_view,
    check_username, check_phone_number, settings_view, registration_success,
    expert_special_feature_view, expert_dashboard_view, join_requests_view  # 
)

urlpatterns = [
    # ✅ الصفحة الرئيسية
    path('', home_view, name='home'),

    # ✅ تسجيل الدخول والخروج
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # ✅ تسجيل مستخدم جديد
    path('register/', register_view, name='register'),
    path('registration-success/', registration_success, name='registration_success'),

    # ✅ لوحة التحكم (عادية وخبراء)
    path('dashboard/', dashboard_view, name='dashboard'),
    path('expert-dashboard/', expert_dashboard_view, name='expert_dashboard'),  # ✅ إضافة لوحة تحكم الخبراء

    # ✅ ميزات الخبراء الخاصة
    path('expert-feature/', expert_special_feature_view, name='expert_special_feature'),

    # ✅ قائمة المستخدمين
    path('list/', users_list, name='users_list'),

    # ✅ الإعدادات
    path('settings/', settings_view, name='settings'),
    path('join-requests/', join_requests_view, name='join_requests'),  # ✅ إضافة هذا السطر هنا


    # ✅ التحقق من توفر اسم المستخدم ورقم الهاتف
    path('check-username/', check_username, name='check_username'),
    path('check-phone/', check_phone_number, name='check_phone_number'),

    # ✅ تغيير كلمة المرور
    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='password_change.html'), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name='password_change_done'),
]
