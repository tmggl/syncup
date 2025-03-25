from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(
        max_length=10,
        required=True,
        help_text="Phone number must start with 05 and be exactly 10 digits."
    )

    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,  #  use choices from the model
        required=True
    )

    profile_image = forms.ImageField(
        required=False,
        help_text="You can upload a profile image or keep the default one."
    )

    class Meta:
        model = CustomUser
        fields = [
            'username',
            'email',
            'phone_number',
            'role',
            'profile_image',
            'password1',
            'password2'
        ]

class ProfileUpdateForm(UserChangeForm):
    password = None  # Hide the password field

    class Meta:
        model = CustomUser
        fields = [
            'username',
            'email',
            'phone_number',
            'role',
            'profile_image'
        ]
