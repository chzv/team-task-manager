# apps/tasks/serializers.py
from rest_framework import serializers
from .models import Team, TaskList, Task

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["id", "name"]

class TaskListSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)
    class Meta:
        model = TaskList
        fields = ["id", "name", "team"]

class TaskSerializer(serializers.ModelSerializer):
    assignee_username = serializers.CharField(source="assignee.username", read_only=True)
    list_name = serializers.CharField(source="list.name", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id", "title", "description", "due_at", "is_done",
            "assignee", "assignee_username",
            "list", "list_name",
        ]
