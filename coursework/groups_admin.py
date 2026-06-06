from django.db.models import Count

from coursework.models import AccessGroup

def build_access_groups_queryset():
    return AccessGroup.objects.annotate(
        keys_count=Count("keys", distinct=True),
        members_count=Count("members", distinct=True),
    ).order_by("name")
