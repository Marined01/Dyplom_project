from django.utils import timezone
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib import messages
from coursework.models import Key, User, Key_requests, Key_return_request, Key_transfer
from django.urls import reverse

from coursework.admin_requests import (
    build_admin_request_queue,
    expire_old_requests,
    get_pending_request_counts,
    normalize_request_type,
)
from coursework.key_metrics import (
    LONG_HELD_DAYS,
    apply_key_sort,
    apply_long_held_filter,
)
from coursework.dashboard import get_dashboard_stats
from coursework.users_admin import (
    USERS_PER_PAGE,
    build_users_queryset,
    keys_held_by_user,
    users_filter_query_string,
)
from coursework.journal import (
    ACTION_TYPES,
    JOURNAL_PER_PAGE,
    build_action_logs,
    export_action_logs_csv,
    journal_filter_query_string,
    parse_journal_filters,
)
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.views.decorators import staff_member_required

def _redirect_after_form(request, default_view="home"):
    """Безпечний редірект після POST (поле next у формі)."""
    next_url = request.POST.get("next", "").strip()
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}
    ):
        return redirect(next_url)
    return redirect(default_view)


def registration_page(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        email = request.POST.get('email')
        password = request.POST.get('password')

        data_error = False

        if User.objects.filter(email=email).exists():
            data_error = True
            messages.error(request, 'Така електронна адреса вже використовується')

        if len(password) < 8:
            data_error = True
            messages.error(request, 'Пароль має містити щонайменше 8 символів')

        if data_error:
            return redirect('registration')

        else:
            new_user = User.objects.create_user(name=name, surname=surname ,email=email, password=password)
            messages.success(request, 'Користувача створено')
            return redirect('login')

    return render(request, 'registration_page.html')

def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Неправильні дані для входу')
            return redirect('login')

    return render(request, 'login_page.html')

@login_required
def logout_page(request):
    logout(request)
    return redirect('login')

@login_required
def home_page(request):
    users_keys = Key.objects.filter(holder=request.user)
    return render(request, 'home_page.html', {'users_keys': users_keys})

@login_required
def key_list(request):
    expire_old_requests()
    keys = Key.objects.select_related("holder").all()
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    allowed_status = {"", "free", "taken", "pending"}
    if status not in allowed_status:
        status = ""
    if status:
        keys = keys.filter(status=status)
    if query:
        keys = keys.filter(
            Q(auditory__icontains=query)
            | Q(holder__name__icontains=query)
            | Q(holder__surname__icontains=query)
            | Q(holder__email__icontains=query)
        ).distinct()

    long_held = request.GET.get("long_held", "").strip() == "1"
    if request.user.is_staff and long_held:
        keys = apply_long_held_filter(keys, True)

    sort = request.GET.get("sort", "").strip()
    if request.user.is_staff:
        keys = apply_key_sort(keys, sort)
    else:
        keys = keys.order_by("auditory")

    has_filters = bool(query or status or long_held or sort)
    return render(
        request,
        "key_list.html",
        {
            "keys": keys,
            "user": request.user,
            "query": query,
            "status_filter": status,
            "sort": sort if request.user.is_staff else "",
            "long_held": long_held and request.user.is_staff,
            "long_held_days": LONG_HELD_DAYS,
            "keys_count": keys.count(),
            "has_filters": has_filters,
        },
    )

@staff_member_required
@require_POST
def take_key(request, key_id):
    try:
        key = Key.objects.get(id=key_id)
    except Key.DoesNotExist:
        raise Http404("Key does not exist")
    try:
        key.take_key(request.user)
        messages.success(request, f"Ключ до аудиторії {key.auditory} видано.")
    except ValueError as e:
        messages.error(request, e)
    return _redirect_after_form(request, default_view="key_list")


@staff_member_required
@require_POST
def put_key(request, key_id):
    """Пряме повернення ключа — лише для персоналу (підтвердження без окремого запиту)."""
    key = get_object_or_404(Key, id=key_id)
    try:
        key.put_key()
        messages.success(request, f"Ключ до аудиторії {key.auditory} повернено.")
    except ValueError as e:
        messages.error(request, e)
    return _redirect_after_form(request, default_view="key_list")

# views.py
@login_required
def transfer_key(request, key_id):
    key = get_object_or_404(Key, id=key_id)

    if key.holder != request.user:
        messages.error(request, "Ви не володієте цим ключем.")
        return redirect('home')

    if request.method == 'POST':
        name = request.POST.get('name')
        surname = request.POST.get('surname')

        try:
            new_holder = User.objects.get(name=name, surname=surname)
        except User.DoesNotExist:
            messages.error(request, 'Користувача не знайдено.')
            return redirect('transfer_key', key_id=key.id)

        existing_request = Key_transfer.objects.filter(
            from_user=request.user, key=key, is_approved=False,
            created_at__gte=timezone.now() - timedelta(minutes=15)
        ).first()
        if existing_request:
            messages.info(request, "Запит вже створено.")
        else:
            Key_transfer.objects.create(from_user=request.user, to_user=new_holder, key=key)
            messages.success(request, "Запит на передачу ключа створено.")

        return redirect('home')

    return render(request, 'transfer_page.html', {'key': key})



@login_required
def my_transfer_requests(request):
    requests = Key_transfer.objects.filter(
        to_user=request.user,
        is_approved=False,
        is_expired=False,
        created_at__gte=timezone.now() - timedelta(minutes=15)
    ).select_related('from_user', 'to_user', 'key')

    return render(request, 'transfer_request.html', {'requests': requests})

@login_required
@require_POST
def approve_transfer_request(request, request_id):
    transfer_request = get_object_or_404(Key_transfer, id=request_id)

    if transfer_request.to_user_id != request.user.id:
        messages.error(request, "Цей запит адресований не вам.")
        return redirect('incoming_transfers')

    if transfer_request.is_valid():
        transfer_request.key.transfer_key(request.user)
        transfer_request.is_approved = True
        transfer_request.save()
        messages.success(request, "Ключ передано вам.")
    else:
        transfer_request.is_expired = True
        transfer_request.save()
        messages.error(request, "Запит недійсний або протермінований.")

    return redirect('incoming_transfers')


@login_required
@require_POST
def reject_transfer_request(request, request_id):
    transfer_request = get_object_or_404(Key_transfer, id=request_id)

    if transfer_request.to_user_id != request.user.id:
        messages.error(request, "Цей запит адресований не вам.")
        return redirect('incoming_transfers')

    if transfer_request.is_expired or transfer_request.is_approved:
        messages.error(request, "Цей запит уже оброблено.")
    else:
        transfer_request.is_expired = True
        transfer_request.save()
        key = transfer_request.key
        key.status = 'taken'
        key.save()
        messages.success(request, f"Запит на передачу ключа {key.auditory} відхилено.")

    return redirect('incoming_transfers')


@login_required
def free_keys(request):
    free_keys = Key.objects.filter(status="free").order_by("auditory")
    query = request.GET.get("q", "").strip()
    if query:
        free_keys = free_keys.filter(auditory__icontains=query)
    return render(
        request,
        "free_keys_page.html",
        {
            "free_keys": free_keys,
            "query": query,
            "free_keys_count": free_keys.count(),
        },
    )

@login_required
def profile(request):
    return render(request, 'profile_page.html', {'user': request.user}  )

@login_required
def profile_edit(request):
    user = request.user
    if request.method == 'POST':
        # user.name = request.POST['name']
        # user.surname = request.POST['surname']
        user.email = request.POST['email']
        password = request.POST.get('password')
        if password:
            user.set_password(password)
        user.save()
        messages.success(request, 'Профіль оновлено успішно.')
        return redirect('home')
    return render(request, 'edit_profile_page.html')


@login_required
@require_POST
def take_key_request(request, key_id):
    key = get_object_or_404(Key, id=key_id)

    if key.status != "free":
        messages.error(request, "Цей ключ недоступний для запиту на видачу.")
        return _redirect_after_form(request)

    existing_request = Key_requests.objects.filter(
        key=key,
        is_approved=False,
        is_expired=False,
        created_at__gte=timezone.now() - timedelta(minutes=15)
    ).first()

    if existing_request:
        messages.error(request, "Ключ вже має активний запит.")
        return _redirect_after_form(request)

    active_keys = Key.objects.filter(holder=request.user, status='taken').count()
    if active_keys >= 4:
        messages.error(request, "Ви не можете мати більше 4 ключів одночасно.")
        return _redirect_after_form(request)

    Key_requests.objects.create(user=request.user, key=key)
    key.status = 'pending'
    key.save()

    messages.success(request, f"Запит на ключ {key.auditory} надіслано адміністратору.")
    return _redirect_after_form(request)


@login_required
@require_POST
def put_key_request(request, key_id):
    key = get_object_or_404(Key, id=key_id)

    if key.holder_id != request.user.id:
        messages.error(request, "Ви не тримаєте цей ключ.")
        return _redirect_after_form(request)

    if key.status != "taken":
        messages.error(request, "Цей ключ не на руках — повернення недоступне.")
        return _redirect_after_form(request)

    existing_request = Key_return_request.objects.filter(
        user=request.user,
        key=key,
        is_expired=False,
        is_approved=False,
        created_at__gte=timezone.now() - timedelta(minutes=15),
    ).exists()

    if existing_request:
        messages.error(request, "Ви вже подали запит на повернення цього ключа.")
        return _redirect_after_form(request)

    Key_return_request.objects.create(user=request.user, key=key)
    messages.success(request, "Запит на повернення ключа надіслано адміністратору.")
    return _redirect_after_form(request)

@staff_member_required
def admin_requests(request):
    expire_old_requests()
    request_type = normalize_request_type(request.GET.get("type", "all"))
    counts = get_pending_request_counts()
    items = build_admin_request_queue(request_type)

    type_labels = {
        "all": "Усі",
        "take": "Видача",
        "return": "Повернення",
    }

    return render(
        request,
        "admin_requests.html",
        {
            "items": items,
            "request_type": request_type,
            "type_labels": type_labels,
            "counts": counts,
            "total_count": counts["take"] + counts["return"],
        },
    )


@staff_member_required
def admin_key_request(request):
    return redirect("admin_requests")


@staff_member_required
def admin_put_request(request):
    return redirect("admin_requests")

@staff_member_required
@require_POST
def approve_key_request(request, request_id):
    key_request = get_object_or_404(Key_requests, id=request_id)

    if key_request.is_valid():
        key = key_request.key
        try:
            key.take_key(key_request.user)
            key_request.is_approved = True
            key_request.save()
            messages.success(request, f"Ключ до {key.auditory} підтверджено.")
        except ValueError as e:
            messages.error(request, str(e))
    else:
        messages.error(request, "Запит недійсний або вже оброблений.")

    return redirect("admin_requests")

@staff_member_required
@require_POST
def approve_return_request(request, request_id):
    return_request = get_object_or_404(Key_return_request, id=request_id)
    if return_request.is_valid():
        return_request.key.put_key()

        return_request.is_approved = True
        return_request.save()
        messages.success(request, f"Ключ {return_request.key.auditory} успішно повернено.")

    else:
        return_request.is_expired = True
        return_request.save()
        messages.error(request, "Час дії запиту минув або вже оброблений.")

    return redirect("admin_requests")

@staff_member_required
@require_POST
def reject_key_request(request, request_id):
    key_request = get_object_or_404(Key_requests, id=request_id)
    key_request.is_expired = True
    key_request.save()

    key = key_request.key
    key.status = 'free'
    key.holder = None
    key.save()

    messages.info(request, f"Запит на ключ {key.auditory} відхилено.")
    return redirect("admin_requests")


@staff_member_required
@require_POST
def reject_return_request(request, request_id):
    return_request = get_object_or_404(Key_return_request, id=request_id)

    return_request.is_expired = True
    return_request.save()

    messages.success(request, f"Запит на повернення ключа {return_request.key.auditory} відхилено.")

    return redirect("admin_requests")

def _dashboard_card_hrefs(cards):
    for card in cards:
        if card.get("url_name"):
            href = reverse(card["url_name"])
            if card.get("query"):
                href = f"{href}?{card['query']}"
            card["href"] = href
        else:
            card["href"] = None


@staff_member_required
def dashboard(request):
    stats = get_dashboard_stats()
    _dashboard_card_hrefs(stats["key_cards"])
    _dashboard_card_hrefs(stats["queue_cards"])
    return render(request, "dashboard.html", stats)


@staff_member_required
def action_view(request):
    query, action_type, date_from, date_to = parse_journal_filters(request)

    logs = build_action_logs(
        query=query,
        action_type=action_type,
        date_from=date_from,
        date_to=date_to,
    )
    paginator = Paginator(logs, JOURNAL_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    has_filters = bool(query or action_type or date_from or date_to)
    filter_query = journal_filter_query_string(
        query, action_type, date_from, date_to
    )

    return render(
        request,
        "action_view.html",
        {
            "page_obj": page_obj,
            "query": query,
            "action_filter": action_type,
            "date_from": date_from,
            "date_to": date_to,
            "action_types": ACTION_TYPES,
            "logs_count": paginator.count,
            "has_filters": has_filters,
            "filter_query": filter_query,
        },
    )


@staff_member_required
def action_view_export(request):
    query, action_type, date_from, date_to = parse_journal_filters(request)
    logs = build_action_logs(
        query=query,
        action_type=action_type,
        date_from=date_from,
        date_to=date_to,
    )
    return export_action_logs_csv(logs)


@staff_member_required
def admin_user_list(request):
    query = request.GET.get("q", "").strip()
    active_filter = request.GET.get("active", "").strip()
    staff_filter = request.GET.get("staff", "").strip()
    if active_filter not in ("", "active", "inactive"):
        active_filter = ""
    if staff_filter not in ("", "staff", "regular"):
        staff_filter = ""

    users = build_users_queryset(query, active_filter, staff_filter)
    paginator = Paginator(users, USERS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))
    filter_qs = users_filter_query_string(query, active_filter, staff_filter)
    has_filters = bool(query or active_filter or staff_filter)

    return render(
        request,
        "admin_user_list.html",
        {
            "page_obj": page_obj,
            "users": page_obj.object_list,
            "query": query,
            "active_filter": active_filter,
            "staff_filter": staff_filter,
            "filter_qs": filter_qs,
            "has_filters": has_filters,
            "users_total": users.count(),
        },
    )


@staff_member_required
def admin_user_edit(request, user_id):
    target = get_object_or_404(User, id=user_id)
    is_self = target.id == request.user.id

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        surname = request.POST.get("surname", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "").strip()

        if not name or not surname or not email:
            messages.error(request, "Ім’я, прізвище та email обов’язкові.")
            return redirect("admin_user_edit", user_id=target.id)

        if User.objects.filter(email=email).exclude(pk=target.pk).exists():
            messages.error(request, "Користувач з таким email уже існує.")
            return redirect("admin_user_edit", user_id=target.id)

        target.name = name
        target.surname = surname
        target.email = email

        if password:
            target.set_password(password)

        if not is_self:
            target.is_active = request.POST.get("is_active") == "on"
            if request.user.is_superuser:
                target.is_staff = request.POST.get("is_staff") == "on"

        target.save()
        messages.success(request, f"Дані користувача {target} оновлено.")
        return redirect("admin_user_list")

    return render(
        request,
        "admin_user_edit.html",
        {
            "target": target,
            "is_self": is_self,
            "keys_held": keys_held_by_user(target),
            "can_edit_staff": request.user.is_superuser,
        },
    )