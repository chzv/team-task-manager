from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/user/$", consumers.UserConsumer.as_asgi()),
    re_path(r"ws/team/(?P<team_id>\d+)/$", consumers.TeamConsumer.as_asgi()),
]
