# apps/tasks/consumers.py
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from .models import Presence, Team

@database_sync_to_async
def _presence_touch(user):
    Presence.objects.update_or_create(user=user, defaults={"last_heartbeat": timezone.now()})

@database_sync_to_async
def _user_allowed(team_id, user):
    return Team.objects.filter(id=team_id, members=user).exists()

class UserConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            await self.close(); return
        self.group = f"user-{user.id}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def receive_json(self, content):
        if content.get("type") == "heartbeat":
            await _presence_touch(self.scope["user"])

    async def disconnect(self, code):
        if hasattr(self, "group"):
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def send_json(self, event):
        await super().send_json(event["payload"])

class TeamConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close(); return
        team_id = int(self.scope["url_route"]["kwargs"]["team_id"])
        if not await _user_allowed(team_id, user):
            await self.close(); return
        self.group = f"team-{team_id}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, "group"):
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def send_json(self, event):
        await super().send_json(event["payload"])
