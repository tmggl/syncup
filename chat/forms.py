from django import forms
from .models import Message


class MessageForm(forms.ModelForm):
    content = forms.CharField(
        label='',
        required=False,
        max_length=2000,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Type your message...',
            'class': 'form-control',
            'style': (
                'width: 100%; '
                'padding: 10px; '
                'border-radius: 6px; '
                'border: 1px solid #ccc; '
                'resize: none; '
                'font-size: 14px;'
            )
        })
    )

    attachment = forms.FileField(
        label='',
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'style': 'margin-top: 10px;'
        })
    )

    class Meta:
        model = Message
        fields = ['content', 'attachment']

    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get("content", "").strip()
        attachment = cleaned_data.get("attachment")

        if not content and not attachment:
            raise forms.ValidationError("You must send a message or attach a file.")

        if content and len(content) > 2000:
            self.add_error('content', "Message is too long (max 2000 characters).")

        return cleaned_data
