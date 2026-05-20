from django.db.models import Count, Q

from coursework.models import Key, User

USERS_PER_PAGE = 25

def build_users_queryset(query="", active_filter="", staff_filter=""):
    qs = User.objects.all()
    if query:
        qs = qs.filter(
            Q(email__icontains=query)
            | Q(name__icontains=query)
            | Q(surname__icontains=query)
        )
    if active_filter == "active":
        qs = qs.filter(is_active=True)
    elif active_filter == "inactive":
        qs = qs.filter(is_active=False)
    if staff_filter == "staff":
        qs = qs.filter(is_staff=True)
    elif staff_filter == "regular":
        qs = qs.filter(is_staff=False)
    return qs.annotate(
        keys_held_count=Count("key", filter=Q(key__status="taken"))
    ).order_by("surname", "name", "email")


def users_filter_query_string(query, active_filter, staff_filter):
    params = {}
    if query:
        params["q"] = query
    if active_filter:
        params["active"] = active_filter
    if staff_filter:
        params["staff"] = staff_filter
    if not params:
        return ""
    from urllib.parse import urlencode

    return urlencode(params)


def keys_held_by_user(user):
    return Key.objects.filter(holder=user, status="taken").order_by("auditory")
