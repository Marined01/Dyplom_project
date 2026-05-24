from datetime import timedelta

from django.db.models import Count
from django.utils import timezone
from coursework.admin_requests import (
    build_admin_request_queue,
    expire_old_requests,
    get_pending_request_counts,
)
from coursework.journal import build_action_logs
from coursework.key_metrics import LONG_HELD_DAYS, long_held_keys_queryset
from coursework.models import Key, User

def status_donut(free, taken, pending):
    total = free + taken + pending
    if total == 0:
        return None
    p_free = round(100 * free / total, 2)
    p_taken = round(100 * taken / total, 2)
    p_pending = round(100 * pending / total, 2)
    stop_free = p_free
    stop_taken = p_free + p_taken
    return {
        "total": total,
        "gradient": (
            f"conic-gradient("
            f"var(--chart-free) 0% {stop_free}%, "
            f"var(--chart-taken) {stop_free}% {stop_taken}%, "
            f"var(--chart-pending) {stop_taken}% 100%"
            f")"
        ),
        "legend": [
            {"label": "Вільні", "value": free, "pct": p_free, "variant": "free"},
            {"label": "Зайняті", "value": taken, "pct": p_taken, "variant": "taken"},
            {"label": "Очікує", "value": pending, "pct": p_pending, "variant": "pending"},
        ],
    }

def activity_bars(days=7):
    logs = build_action_logs()
    today = timezone.localdate()
    labels = []
    counts = []
    for offset in range(days - 1, -1, -1):
        day = today - timedelta(days=offset)
        labels.append(day.strftime("%d.%m"))
        counts.append(
            sum(1 for row in logs if timezone.localtime(row["timestamp"]).date() == day)
        )
    peak = max(counts) if counts else 0
    bars = []
    for label, count in zip(labels, counts):
        height = round(100 * count / peak) if peak else 0
        bars.append({"label": label, "count": count, "height_pct": max(height, 4) if count else 0})
    return bars


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
            "url_name": "admin_user_list",
            "query": "active=active",
            "variant": "neutral",
        },
    ]

    return {
        "key_cards": key_cards,
        "queue_cards": queue_cards,
        "pending_take": pending_take,
        "pending_return": pending_return,
        "pending_total": pending_total,
        "long_held_keys": list(long_held_qs[:10]),
        "long_held_count": long_held_count,
        "long_held_days": LONG_HELD_DAYS,
        "status_donut": status_donut(keys_free, keys_taken, keys_pending),
        "activity_bars": activity_bars(),
        "recent_pending": build_admin_request_queue("all")[:5],
        "recent_activity": build_action_logs()[:6],
    }
