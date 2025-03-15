from django.contrib import admin
from .models import Meeting, ExpertAvailability

class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'expert', 'meeting_link', 'created_at')
    list_filter = ('date', 'expert')
    search_fields = ('title', 'expert__username', 'participants__username')
    filter_horizontal = ('participants',)  # تحسين اختيار المشاركين في الاجتماع

class ExpertAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('expert', 'date', 'start_time', 'end_time', 'is_booked')
    list_filter = ('date', 'expert', 'is_booked')
    search_fields = ('expert__username',)

admin.site.register(Meeting, MeetingAdmin)
admin.site.register(ExpertAvailability, ExpertAvailabilityAdmin)