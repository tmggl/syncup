from django.contrib import admin
from .models import Diagram

# تخصيص عرض المخططات في Django Admin
class DiagramAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'created_by', 'created_at')
    list_filter = ('project',)
    search_fields = ('name', 'created_by__username')

admin.site.register(Diagram, DiagramAdmin)
