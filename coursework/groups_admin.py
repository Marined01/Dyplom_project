from django.db.models import Count

from coursework.models import AccessGroup, Key


def build_access_groups_queryset():
    return AccessGroup.objects.annotate(
        keys_count=Count("keys", distinct=True),
        members_count=Count("members", distinct=True),
    ).order_by("name")

def all_access_groups():
    return AccessGroup.objects.order_by("name")

def parse_user_access_post(request):
    group_ids = []
    extra_key_ids = []
    for raw_id in request.POST.getlist("access_groups"):
        try:
            group_ids.append(int(raw_id))
        except (TypeError, ValueError):
            continue
    for raw_id in request.POST.getlist("allowed_keys"):
        try:
            extra_key_ids.append(int(raw_id))
        except (TypeError, ValueError):
            continue
    return group_ids, extra_key_ids
def user_access_form_context(target, *, group_ids=None, extra_key_ids=None):
    if group_ids is not None:
        selected_group_ids = set(group_ids)
    else:
        selected_group_ids = set(target.access_groups.values_list("pk", flat=True))

    if extra_key_ids is not None:
        selected_extra_key_ids = set(extra_key_ids)
    else:
        selected_extra_key_ids = set(target.allowed_keys.values_list("pk", flat=True))

    return {
        "all_access_groups": all_access_groups(),
        "all_keys_for_access": Key.objects.order_by("auditory"),
        "selected_group_ids": selected_group_ids,
        "selected_extra_key_ids": selected_extra_key_ids,
    }


def save_user_access(target, group_ids, extra_key_ids):
    target.access_groups.set(AccessGroup.objects.filter(pk__in=group_ids))
    target.allowed_keys.set(Key.objects.filter(pk__in=extra_key_ids))
