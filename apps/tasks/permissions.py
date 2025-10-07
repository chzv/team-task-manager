from rest_framework import permissions
from .models import Team, TaskList, Task

def _obj_team(obj):
    if isinstance(obj, Team): return obj
    if isinstance(obj, TaskList): return obj.team
    if isinstance(obj, Task): return obj.list.team
    return None

class IsTeamMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        team = _obj_team(obj)
        return team and team.members.filter(id=request.user.id).exists()
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
