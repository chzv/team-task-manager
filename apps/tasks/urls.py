from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path("", lambda r: redirect("team-board", team_id=1), name="home"),
    path("team/<int:team_id>/", views.team_board, name="team-board"),
]
