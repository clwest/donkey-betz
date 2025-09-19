from django.contrib import admin
from .models import AIStrategy, GeneratedProject, ProjectFile, ProjectDeployment


@admin.register(AIStrategy)
class AIStrategyAdmin(admin.ModelAdmin):
    list_display = ['title', 'strategy_type', 'potential_revenue', 'difficulty', 'final_score', 'discovered_date']
    list_filter = ['strategy_type', 'difficulty', 'source']
    search_fields = ['title', 'description']
    ordering = ['-final_score', '-discovered_date']


@admin.register(GeneratedProject)
class GeneratedProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'project_type', 'user', 'status', 'revenue_potential', 'ready_to_launch', 'created_at']
    list_filter = ['status', 'project_type', 'ready_to_launch']
    search_fields = ['name', 'description']
    ordering = ['-created_at']
    raw_id_fields = ['user', 'strategy']


@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ['filename', 'project', 'file_type', 'file_size', 'updated_at']
    list_filter = ['file_type']
    search_fields = ['filename', 'project__name']
    ordering = ['project', 'filename']
    raw_id_fields = ['project']


@admin.register(ProjectDeployment)
class ProjectDeploymentAdmin(admin.ModelAdmin):
    list_display = ['project', 'is_deployed', 'deployment_platform', 'actual_revenue', 'last_run']
    list_filter = ['is_deployed', 'deployment_platform', 'has_openai_key']
    search_fields = ['project__name']
    ordering = ['-deployed_at']
    raw_id_fields = ['project']