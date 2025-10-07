from rest_framework import viewsets, permissions, decorators, response, status
from django.db.models import Q
from django.contrib.auth.models import User
from django.conf import settings
from .models import Team, TaskList, Task, TelegramLink
from .serializers import TeamSerializer, TaskListSerializer, TaskSerializer
from .permissions import IsTeamMember
from .services.events import emit_task_event
from rest_framework.views import APIView
from django.views.decorators.csrf import ensure_csrf_cookie
from .tasks import notify_assigned_task

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]
    def perform_create(self, serializer):
        team = serializer.save()
        team.members.add(self.request.user)

class TaskListViewSet(viewsets.ModelViewSet):
    serializer_class = TaskListSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeamMember]
    queryset = TaskList.objects.select_related("team")

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeamMember]
    queryset = Task.objects.select_related("list", "assignee", "list__team")

    def get_queryset(self):
        qs = super().get_queryset().filter(list__team__members=self.request.user)

        # ?list=<id>
        list_id = self.request.query_params.get("list")
        if list_id:
            qs = qs.filter(list_id=list_id)

        # ?filter=me|open|all
        flt = self.request.query_params.get("filter")
        if flt == "me":
            qs = qs.filter(assignee=self.request.user, is_done=False)
        elif flt == "open":
            qs = qs.filter(is_done=False)

        # ?q=<substring>
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(title__icontains=q)

        return qs.order_by("-id")

    def perform_create(self, serializer):
        task = serializer.save(created_by=self.request.user)
        if task.assignee_id:
            notify_assigned_task.delay(task.id, task.assignee_id)
        emit_task_event(task, "created")

    def perform_update(self, serializer):
        old = Task.objects.get(pk=self.get_object().pk)
        task = serializer.save()
        if task.assignee_id and task.assignee_id != old.assignee_id:
            notify_assigned_task.delay(task.id, task.assignee_id)
        emit_task_event(task, "updated")
         
    @decorators.action(detail=True, methods=["post"])
    def done(self, request, pk=None):
        task = self.get_object()
        task.is_done = True
        task.save(update_fields=["is_done","updated_at"])
        emit_task_event(task, "updated")
        return response.Response({"status":"ok"})

    @decorators.action(detail=False, methods=["get"])
    def my(self, request):
        qs = self.get_queryset().filter(assignee=request.user, is_done=False)
        data = TaskSerializer(qs, many=True).data
        return response.Response(data)

# ---- Telegram link endpoints ----
from rest_framework.response import Response
from rest_framework import status

class CreateTGCode(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        if request.headers.get("Authorization") != f"Bearer {settings.SERVICE_TOKEN}":
            return Response({"detail": "forbidden"}, status=status.HTTP_403_FORBIDDEN)

        tg_user_id = request.data.get("tg_user_id")
        if not tg_user_id:
            return Response({"detail": "tg_user_id is required"}, status=400)

        import random, string
        code = "".join(random.choices(string.digits, k=6))

        link, _ = TelegramLink.objects.get_or_create(
            tg_user_id=tg_user_id, defaults={"user": None}
        )
        link.one_time_code = code
        link.save(update_fields=["one_time_code"])
        return Response({"code": code}, status=200)

class ConfirmTGLink(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        code = request.data.get("code")
        link = TelegramLink.objects.filter(one_time_code=code).first()
        if not link:
            return response.Response({"detail": "Invalid code"}, status=400)
        link.user = request.user
        link.one_time_code = None
        link.save()
        return response.Response({"status":"linked"})

class TGProxyUserAPIView(APIView):
    """
    Проксируем запросы бота к методам, где нужно знать пользователя по tg_user_id.
    """
    authentication_classes = []  # проверяем сервисный токен
    permission_classes = []
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if request.headers.get("Authorization") != f"Bearer {settings.SERVICE_TOKEN}":
            self.permission_denied(request)
    def get_user(self, request):
        tg_id = request.headers.get("X-TG-USER")
        link = TelegramLink.objects.filter(tg_user_id=tg_id, user__isnull=False).select_related("user").first()
        return link.user if link else None

class TGMyTasks(TGProxyUserAPIView):
    def get(self, request):
        user = self.get_user(request)
        if not user:
            return response.Response([], status=200)
        qs = Task.objects.filter(assignee=user, is_done=False, list__team__members=user)
        return response.Response(TaskSerializer(qs, many=True).data)

class TGMarkDone(TGProxyUserAPIView):
    def post(self, request, task_id):
        user = self.get_user(request)
        if not user:
            return response.Response(status=403)
        task = Task.objects.filter(id=task_id, assignee=user, list__team__members=user).first()
        if not task:
            return response.Response(status=404)
        task.is_done = True
        task.save(update_fields=["is_done","updated_at"])
        emit_task_event(task, "updated")
        return response.Response({"status":"ok"})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import Team, TaskList

@ensure_csrf_cookie
@login_required
def team_board(request, team_id: int):
    team = get_object_or_404(Team.objects.prefetch_related("members"), id=team_id, members=request.user)
    lists = TaskList.objects.filter(team=team).order_by("id")
    members = User.objects.filter(id__in=team.members.values_list("id", flat=True)).order_by("username")
    return render(request, "tasks.html", {"team": team, "lists": lists, "members": members})
