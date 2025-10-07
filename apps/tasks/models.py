from django.conf import settings
from django.db import models

class Team(models.Model):
    name = models.CharField(max_length=128)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="teams")
    def __str__(self): return self.name

class TaskList(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="lists")
    name = models.CharField(max_length=128)
    def __str__(self): return f"{self.team} / {self.name}"

class Task(models.Model):
    list = models.ForeignKey(TaskList, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    is_done = models.BooleanField(default=False)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="assigned_tasks"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_tasks"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Presence(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    last_heartbeat = models.DateTimeField(auto_now=True)

class TelegramLink(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,        
    )
    tg_user_id = models.BigIntegerField(
        unique=True,
        null=True, blank=True         
    )
    one_time_code = models.CharField(max_length=16, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class NotificationLog(models.Model):
    KINDS = (("assigned","assigned"),("overdue","overdue"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    kind = models.CharField(max_length=32, choices=KINDS)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ("user","task","kind")
