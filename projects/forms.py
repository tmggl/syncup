from django import forms
from .models import Project, ProjectType, ProjectAttachment, ProjectInvitation, JoinRequest
from users.models import CustomUser

class ProjectForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=ProjectType.objects.all(), 
        empty_label="Select Project Type", 
        required=True
    )
    members = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.none(),  # نضبطه لاحقًا في __init__
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select team members"
    )
    logo = forms.ImageField(required=False, help_text="Upload project logo")
    
    attachments = forms.FileField(
        required=False, 
        help_text="Upload multiple project attachments"
    )

    project_color = forms.ChoiceField(
        choices=Project.COLOR_CHOICES,
        widget=forms.Select,
        required=True,
        help_text="Select a color for the project"
    )

    def __init__(self, *args, **kwargs):
        project_instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

        if project_instance:
            self.fields['members'].queryset = project_instance.members.all()
        else:
            self.fields['members'].queryset = CustomUser.objects.none()

    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'end_date', 'category', 'members', 'logo', 'attachments', 'project_color']


class ProjectAttachmentForm(forms.ModelForm):
    file = forms.FileField(
        required=False,
        help_text="Upload multiple files"
    )
    
    class Meta:
        model = ProjectAttachment
        fields = ['file']

class ProjectInvitationForm(forms.ModelForm):
    class Meta:
        model = ProjectInvitation
        fields = ['project', 'invited_user', 'status']

class JoinRequestForm(forms.ModelForm):
    class Meta:
        model = JoinRequest
        fields = ['project', 'status']
