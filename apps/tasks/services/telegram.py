# apps/tasks/services/telegram.py
import os
import logging
import requests
from django.conf import settings

log = logging.getLogger(__name__)

def send_tg_message_if_needed(chat_id: int, text: str) -> bool:
    token = getattr(settings, "BOT_TOKEN", "") or os.getenv("BOT_TOKEN", "")
    if not token:
        log.warning("TG: BOT_TOKEN is empty — skip")
        return False
    if not chat_id:
        log.warning("TG: chat_id is empty — skip")
        return False

    try:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=8,
        )
        if r.status_code != 200:
            log.error("TG send failed: %s %s", r.status_code, r.text[:300])
            return False
        return True
    except Exception:
        log.exception("TG send exception")
        return False
