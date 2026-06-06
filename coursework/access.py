# Access check

from django.db.models import Q

from coursework.models import Key


def user_has_any_access(user) -> bool:
    if user.is_staff:
        return True
    if user.allowed_keys.exists():
        return True
    if user.access_groups.exists():
        return True
    return False


def user_can_access_key(user, key) -> bool:
    if user.is_staff:
        return True
    if user.allowed_keys.filter(pk=key.pk).exists():
        return True
    if user.access_groups.filter(keys=key).exists():
        return True
    return False


def keys_queryset_for_user(user):
    if user.is_staff:
        return Key.objects.all()
    from_groups = Key.objects.filter(access_groups__members=user)
    personal = user.allowed_keys.all()
    return Key.objects.filter(
        Q(pk__in=from_groups.values_list("pk", flat=True))
        | Q(pk__in=personal.values_list("pk", flat=True))
    ).distinct()
