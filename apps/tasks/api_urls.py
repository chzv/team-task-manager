from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamViewSet, TaskListViewSet, TaskViewSet, CreateTGCode, ConfirmTGLink, TGMyTasks, TGMarkDone

router = DefaultRouter()
router.register(r"teams", TeamViewSet)
router.register(r"lists", TaskListViewSet)
router.register(r"tasks", TaskViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("telegram/create_code/", CreateTGCode.as_view()),
    path("telegram/confirm_link/", ConfirmTGLink.as_view()),
    path("tasks/my/", TaskViewSet.as_view({"get": "my"})),
    path("tg/tasks/", TGMyTasks.as_view()),
    path("tg/tasks/<int:task_id>/done/", TGMarkDone.as_view()),
]
