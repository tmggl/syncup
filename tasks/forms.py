from django import forms
from .models import Task
from projects.models import Project
from django.contrib.auth import get_user_model
from django.forms.widgets import DateInput

CustomUser = get_user_model()

class TaskForm(forms.ModelForm):
    project = forms.ModelChoiceField(
        queryset=Project.objects.none(),
        empty_label="Select a project...",
        label="Project"
    )

    class Meta:
        model = Task
        fields = ['project', 'title', 'description', 'assigned_to', 'due_date', 'files']
        labels = {
            'title': 'Task Title',
            'description': 'Task Description',
            'assigned_to': 'Assign To',
            'due_date': 'Due Date',
            'files': 'Attach Files',
        }
        help_texts = {
            'title': 'Enter the task title.',
            'description': 'Provide a brief description of the task.',
            'assigned_to': 'Select the user who will be responsible for this task.',
            'due_date': 'Choose the deadline for the task.',
            'files': 'Upload any relevant files for this task (optional).',
        }
        widgets = {
            'due_date': DateInput(attrs={'type': 'date'})  # ✅ لتفعيل التقويم في حقل التاريخ
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # ✅ Extract the user
        selected_project = kwargs.pop('selected_project', None)  # ✅ Extract selected project if provided
        super().__init__(*args, **kwargs)

        if user:
            self.fields['project'].queryset = Project.objects.filter(owner=user)

        # ✅ Filter assigned_to only if project is selected
        if selected_project:
            self.fields['assigned_to'].queryset = selected_project.members.all()
        else:
            self.fields['assigned_to'].queryset = CustomUser.objects.none()
