from django.contrib import admin
from .models import AIStrategy


@admin.register(AIStrategy)
class AIStrategyAdmin(admin.ModelAdmin):
    list_display = ['title', 'strategy_type', 'potential_revenue', 'difficulty', 'final_score', 'discovered_date']
    list_filter = ['strategy_type', 'difficulty', 'source']
    search_fields = ['title', 'description']
    ordering = ['-final_score', '-discovered_date']
