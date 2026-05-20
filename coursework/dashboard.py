"""Показники для інформаційної панелі (дашборд) адміністратора."""

from django.db.models import Count

from coursework.admin_requests import expire_old_requests, get_pending_request_counts
from coursework.key_metrics import LONG_HELD_DAYS, long_held_keys_queryset
from coursework.models import Key, User


def get_dashboard_stats():
    # Збирає цифри для карток дашборду.
    # Повертає dict із групами key_cards та queue_cards (списки словників для шаблону).

    expire_old_requests()

    key_counts = {
        row["status"]: row["count"]
        for row in Key.objects.values("status").annotate(count=Count("id"))
    }
    keys_free = key_counts.get("free", 0)
    keys_taken = key_counts.get("taken", 0)
    keys_pending = key_counts.get("pending", 0)
    keys_total = keys_free + keys_taken + keys_pending

    pending_counts = get_pending_request_counts()
    pending_take = pending_counts["take"]
    pending_return = pending_counts["return"]
    pending_total = pending_take + pending_return

    users_active = User.objects.filter(is_active=True).count()
    long_held_qs = long_held_keys_queryset()
    long_held_count = long_held_qs.count()

    key_cards = [
        {
            "label": "Усього аудиторій",
            "value": keys_total,
            "url_name": "key_list",
            "variant": "neutral",
        },
        {
            "label": "Вільні",
            "value": keys_free,
            "url_name": "key_list",
            "query": "status=free",
            "variant": "success",
        },
        {
            "label": "Зайняті",
            "value": keys_taken,
            "url_name": "key_list",
            "query": "status=taken",
            "variant": "info",
        },
        {
            "label": "Очікує видачі",
            "value": keys_pending,
            "url_name": "key_list",
            "query": "status=pending",
            "variant": "warning",
            "hint": "Статус ключа в таблиці (після запиту на видачу)",
        },
        {
            "label": f"Довго на руках (≥{LONG_HELD_DAYS} дн.)",
            "value": long_held_count,
            "url_name": "key_list",
            "query": "status=taken&long_held=1&sort=held",
            "variant": "warning",
            "hint": "Зайняті без повернення довше порогу",
        },
    ]

    queue_cards = [
        {
            "label": "Запити адміна (усього)",
            "value": pending_total,
            "url_name": "admin_requests",
            "variant": "accent" if pending_total else "neutral",
            "hint": "Видача + повернення, що чекають рішення",
        },
        {
            "label": "запитів на видачу",
            "value": pending_take,
            "url_name": "admin_requests",
            "query": "type=take",
            "variant": "neutral",
        },
        {
            "label": "запитів на повернення",
            "value": pending_return,
            "url_name": "admin_requests",
            "query": "type=return",
            "variant": "neutral",
        },
        {
            "label": "Активних користувачів",
            "value": users_active,
            "url_name": None,
            "variant": "neutral",
        },
    ]

    return {
        "key_cards": key_cards,
        "queue_cards": queue_cards,
        "pending_take": pending_take,
        "pending_return": pending_return,
        "long_held_keys": list(long_held_qs[:10]),
        "long_held_count": long_held_count,
        "long_held_days": LONG_HELD_DAYS,
    }
