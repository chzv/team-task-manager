from django.contrib import admin
from .models import Task, TaskList, Team, NotificationLog, TelegramLink, Presence

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "list", "assignee", "is_done", "due_at")
    list_filter = ("is_done", "list")
    search_fields = ("title", "description")
    autocomplete_fields = ("list", "assignee", "created_by")

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(TaskList)
class TaskListAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "team")
    search_fields = ("name",)
    autocomplete_fields = ("team",)   

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    filter_horizontal = ("members",)
    search_fields = ("name",) 

admin.site.register(NotificationLog)
admin.site.register(TelegramLink)
admin.site.register(Presence)
