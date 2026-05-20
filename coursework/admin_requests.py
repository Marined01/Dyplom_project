"""Черга запитів адміністратора (видача + повернення)."""

from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from coursework.models import Key, Key_requests, Key_return_request

REQUEST_WINDOW = timedelta(minutes=15)


def normalize_request_type(request_type):
    request_type = (request_type or "all").strip()
    if request_type not in ("all", "take", "return"):
        return "all"
    return request_type


def _active_take_queryset():
    since = timezone.now() - REQUEST_WINDOW
    return Key_requests.objects.filter(
        is_approved=False,
        is_expired=False,
        created_at__gte=since,
    ).select_related("key", "user")


def _active_return_queryset():
    since = timezone.now() - REQUEST_WINDOW
    return Key_return_request.objects.filter(
        is_approved=False,
        is_expired=False,
        created_at__gte=since,
    ).select_related("key", "user")


def get_pending_request_counts():
    return {
        "take": _active_take_queryset().count(),
        "return": _active_return_queryset().count(),
    }


def expire_old_requests():
    """Позначити прострочені запити та звільнити ключі без активного запиту на видачу."""
    since = timezone.now() - REQUEST_WINDOW

    Key_requests.objects.filter(
        is_approved=False,
        is_expired=False,
        created_at__lt=since,
    ).update(is_expired=True)

    Key_return_request.objects.filter(
        is_approved=False,
        is_expired=False,
        created_at__lt=since,
    ).update(is_expired=True)

    active_take_key_ids = _active_take_queryset().values_list("key_id", flat=True)
    Key.objects.filter(status="pending").exclude(
        id__in=active_take_key_ids
    ).update(status="free", holder=None)


def build_admin_request_queue(request_type="all"):
    """
    Єдиний список активних запитів для адміна.
    request_type: all | take | return
    """
    request_type = normalize_request_type(request_type)

    items = []

    if request_type in ("all", "take"):
        for req in _active_take_queryset():
            items.append(
                {
                    "kind": "take",
                    "kind_label": "Видача",
                    "id": req.id,
                    "created_at": req.created_at,
                    "user": req.user,
                    "key": req.key,
                    "approve_url": reverse(
                        "approve_take_request", args=[req.id]
                    ),
                    "reject_url": reverse(
                        "reject_key_request", args=[req.id]
                    ),
                }
            )

    if request_type in ("all", "return"):
        for req in _active_return_queryset():
            items.append(
                {
                    "kind": "return",
                    "kind_label": "Повернення",
                    "id": req.id,
                    "created_at": req.created_at,
                    "user": req.user,
                    "key": req.key,
                    "approve_url": reverse(
                        "approve_put_request", args=[req.id]
                    ),
                    "reject_url": reverse(
                        "reject_put_request", args=[req.id]
                    ),
                    "approve_label": "Підтвердити повернення",
                }
            )

    for item in items:
        if "approve_label" not in item:
            item["approve_label"] = "Підтвердити"

    items.sort(key=lambda x: x["created_at"], reverse=True)
    return items
