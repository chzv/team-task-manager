from celery import shared_task
from django.utils import timezone
from .models import Task, Presence, NotificationLog, TelegramLink
from .services.telegram import send_tg_message_if_needed
from django.conf import settings

def _web_active(user_id, seconds=None):
    ttl = int(getattr(settings, "WEB_PRESENCE_TTL_SEC", 30)) if seconds is None else seconds
    p = Presence.objects.filter(user_id=user_id).first()
    from django.utils import timezone
    return bool(p and (timezone.now() - p.last_heartbeat).total_seconds() < ttl)

@shared_task(name="apps.tasks.tasks.notify_assigned_task")
def notify_assigned_task(task_id: int, user_id: int) -> None:
    link = TelegramLink.objects.filter(user_id=user_id).first()
    if link and not _web_active(user_id):
        send_tg_message_if_needed(link.tg_user_id, f"Вам назначена задача #{task_id}")
    NotificationLog.objects.get_or_create(user_id=user_id, task_id=task_id, kind="assigned")

@shared_task(name="apps.tasks.tasks.check_overdue")
def check_overdue() -> None:
    now = timezone.now()
    qs = Task.objects.filter(is_done=False, due_at__lt=now)
    for t in qs:
        if not t.assignee_id:
            continue
        exists = NotificationLog.objects.filter(user=t.assignee, task=t, kind="overdue").exists()
        if not exists:
            link = TelegramLink.objects.filter(user=t.assignee).first()
            if link and not _web_active(t.assignee_id):
                send_tg_message_if_needed(link.tg_user_id, f"Просрочен срок: {t.title}")
            NotificationLog.objects.create(user=t.assignee, task=t, kind="overdue")
