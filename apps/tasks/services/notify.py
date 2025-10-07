# apps/tasks/services/notify.py  (чистая версия)
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import requests
from django.utils import timezone
from .models import Presence, TelegramLink, NotificationLog, Task

channel_layer = get_channel_layer()

def _web_notify(user_id: int, payload: dict):
    if not channel_layer:
        return
    async_to_sync(channel_layer.group_send)(
        f"user-{user_id}",
        {"type": "send.json", "payload": payload},
    )

def _tg_notify(user_id: int, text: str):
    if not settings.BOT_TOKEN:
        return
    link = TelegramLink.objects.filter(user_id=user_id, tg_user_id__isnull=False).first()
    if not link:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage",
            json={"chat_id": link.tg_user_id, "text": text, "parse_mode": "HTML"},
            timeout=5,
        )
    except Exception:
        pass

def _user_online(user_id: int) -> bool:
    pr = Presence.objects.filter(user_id=user_id).first()
    return bool(pr) and (timezone.now() - pr.last_heartbeat).total_seconds() <= 30

def notify_assigned(task: Task):
    if not task.assignee_id:
        return
    _, created = NotificationLog.objects.get_or_create(
        user_id=task.assignee_id, task=task, kind="assigned"
    )
    if not created:
        return
    title = f"Новая задача #{task.id}: {task.title}"
    _web_notify(task.assignee_id, {"type": "notify", "text": title})
    if not _user_online(task.assignee_id):
        _tg_notify(task.assignee_id, f"🆕 {title}")

def notify_overdue(task: Task):
    if not task.assignee_id:
        return
    _, created = NotificationLog.objects.get_or_create(
        user_id=task.assignee_id, task=task, kind="overdue"
    )
    if not created:
        return
    title = f"⏰ Просрочено #{task.id}: {task.title}"
    _web_notify(task.assignee_id, {"type": "notify", "text": title})
    if not _user_online(task.assignee_id):
        _tg_notify(task.assignee_id, title)
