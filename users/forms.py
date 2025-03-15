from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

# ✅ نموذج تسجيل مستخدم جديد
class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(
        max_length=10,
        required=True,
        help_text="رقم الجوال يجب أن يبدأ بـ 05 ويكون مكونًا من 10 أرقام."
    )
    role = forms.ChoiceField(
        choices=[('admin', 'Admin'), ('manager', 'Manager'), ('member', 'Member')], 
        required=True
    )
    profile_image = forms.ImageField(
        required=False,  # السماح للمستخدم بعدم رفع صورة أثناء التسجيل
        help_text="يمكنك رفع صورة شخصية، أو سيتم تعيين صورة افتراضية."
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'role', 'profile_image', 'password1', 'password2']

# ✅ نموذج تحديث بيانات المستخدم (للاستخدام في صفحة الإعدادات)
class ProfileUpdateForm(UserChangeForm):
    password = None  # منع تعديل كلمة المرور في هذا النموذج

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'role', 'profile_image']
