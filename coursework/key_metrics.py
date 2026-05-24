from datetime import timedelta

from django.db.models import DurationField, F
from django.db.models.functions import Now
from django.db.models.expressions import ExpressionWrapper
from django.utils import timezone

from coursework.models import Key

LONG_HELD_DAYS = 1
ALLOWED_SORT = {"", "auditory", "status", "held", "-held"}


def long_held_keys_queryset():
    cutoff = timezone.now() - timedelta(days=LONG_HELD_DAYS)
    return (
        Key.objects.filter(
            status="taken",
            take_key_time__isnull=False,
            take_key_time__lte=cutoff,
        )
        .select_related("holder")
        .order_by("take_key_time")
    )

def apply_long_held_filter(queryset, enabled):
    if not enabled:
        return queryset
    cutoff = timezone.now() - timedelta(days=LONG_HELD_DAYS)
    return queryset.filter(
        status="taken",
        take_key_time__isnull=False,
        take_key_time__lte=cutoff,
    )

def apply_key_sort(queryset, sort):
    sort = (sort or "").strip()
    if sort not in ALLOWED_SORT:
        sort = ""

    if sort in ("held", "-held"):
        queryset = queryset.annotate(
            _held_duration=ExpressionWrapper(
                Now() - F("take_key_time"),
                output_field=DurationField(),
            )
        )
        order = "-_held_duration" if sort == "held" else "_held_duration"
        return queryset.order_by(order, "auditory")

    if sort == "status":
        return queryset.order_by("status", "auditory")
    return queryset.order_by("auditory")
