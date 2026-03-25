from django.contrib import admin

from .models import Workspace


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'owner', 'created_at']
    search_fields = ['name']
    raw_id_fields = ['owner']
    filter_horizontal = ['members']
