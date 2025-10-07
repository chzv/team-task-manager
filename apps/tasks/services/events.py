from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def emit_task_event(task, action: str):
    layer = get_channel_layer()
    payload = {
        "type": "send_json",
        "payload": {
            "action": action,
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_done": task.is_done,
                "assignee": task.assignee_id,
                "due_at": task.due_at.isoformat() if task.due_at else None,
                "list": task.list_id,
                "team": task.list.team_id,
            }
        }
    }
    async_to_sync(layer.group_send)(f"team-{task.list.team_id}", payload)
    if task.assignee_id:
        async_to_sync(layer.group_send)(f"user-{task.assignee_id}", payload)
