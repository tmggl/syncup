from django import forms
from django.utils import timezone
from meetings.models import Meeting
from projects.models import Project
from users.models import CustomUser

class ManualMeetingForm(forms.ModelForm):
    participants = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Select Participants"
    )

    class Meta:
        model = Meeting
        fields = ['project', 'title', 'date', 'time', 'meeting_link', 'platform', 'description', 'participants']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields['project'].queryset = Project.objects.filter(owner=self.user)

        self.fields['project'].required = True

        # عند اختيار المشروع، نظهر أعضاءه في participants
        if 'project' in self.data:
            try:
                project_id = int(self.data.get('project'))
                project = Project.objects.get(id=project_id)
                self.fields['participants'].queryset = project.members.all()
            except (ValueError, Project.DoesNotExist):
                pass
        elif self.instance and self.instance.project:
            self.fields['participants'].queryset = self.instance.project.members.all()

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date < timezone.localdate():
            raise forms.ValidationError("Meeting date cannot be in the past.")
        return date

    def clean_participants(self):
        participants = self.cleaned_data.get('participants')
        project = self.cleaned_data.get('project')

        if not project:
            return participants

        # إضافة المالك تلقائيًا إلى القائمة
        owner = project.owner

        # قائمة المشاركين الفعلية (مع المالك مضاف)
        final_participants = list(participants) if participants else []
        if owner not in final_participants:
            final_participants.append(owner)

        if len(final_participants) < 2:
            raise forms.ValidationError("You must select at least one participant in addition to the project owner.")

        return final_participants
