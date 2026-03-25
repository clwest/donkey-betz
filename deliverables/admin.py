from django.contrib import admin

from .models import Deliverable


@admin.register(Deliverable)
class DeliverableAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'status', 'workspace', 'user', 'created_at']
    list_filter = ['status', 'workspace']
    search_fields = ['title', 'description']
    raw_id_fields = ['user', 'workspace']
