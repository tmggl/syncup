from django.db import models
from users.models import CustomUser

class ProjectType(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Project type defined by admin

    def __str__(self):
        return self.name

class Project(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    COLOR_CHOICES = [
        ('purple', 'Purple'),
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('orange', 'Orange'),
        ('pink', 'Pink'),
    ]

    name = models.CharField(max_length=255)  # Project name
    description = models.TextField(blank=True, null=True)  # Project description
    start_date = models.DateField()  # Start date
    end_date = models.DateField(blank=True, null=True)  # End date
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='owned_projects')  # Project owner
    members = models.ManyToManyField(CustomUser, related_name='projects', blank=True)  # Project members
    created_at = models.DateTimeField(auto_now_add=True)  # Creation date
    category = models.ForeignKey(ProjectType, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')  # Project status
    logo = models.ImageField(upload_to='project_logos/', blank=True, null=True)  # Project logo
    project_color = models.CharField(max_length=10, choices=COLOR_CHOICES, default='blue')  # Project color

    def __str__(self):
        return self.name

    def is_manager(self, user):
        """Check if the user is the project manager (owner)."""
        return self.owner == user

    def add_member(self, user):
        """Add a member to the project."""
        self.members.add(user)
        return True

    def update_progress(self):
        """Calculate project progress based on completed tasks."""
        total_tasks = self.tasks.count()  # Total number of tasks
        completed_tasks = self.tasks.filter(status='completed').count()  # Completed tasks

        if total_tasks > 0:
            self.progress = int((completed_tasks / total_tasks) * 100)
        else:
            self.progress = 0  # If no tasks, progress is 0%

        self.save()  # Save the updates

class ProjectAttachment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='project_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.project.name} uploaded on {self.uploaded_at}"

class ProjectInvitation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='invitations')
    invited_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='project_invitations')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')],
        default='pending'
    )

    def __str__(self):
        return f"Invitation to {self.invited_user.username} for {self.project.name}"

class JoinRequest(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="join_requests")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sent_join_requests")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        default='pending'
    )

    def __str__(self):
        return f"Join request from {self.user.username} to {self.project.name}"

class Meeting(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='meetings')  # Related project
    expert = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='meetings_as_expert')  # Assigned expert
    date = models.DateTimeField()  # Meeting date and time
    created_at = models.DateTimeField(auto_now_add=True)  # Creation timestamp

    def __str__(self):
        return f"Meeting for {self.project.name} with {self.expert.username} on {self.date}"
