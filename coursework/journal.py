import csv
from io import StringIO
from urllib.parse import urlencode

from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_date

from coursework.models import Key_requests, Key_return_request, Key_transfer

JOURNAL_PER_PAGE = 25

ACTION_TYPES = (
    ("", "Усі типи"),
    ("take", "Видача"),
    ("return", "Повернення"),
    ("transfer", "Передача"),
)

ACTION_LABELS = {
    "take": "Видача",
    "return": "Повернення",
    "transfer": "Передача",
}


def _apply_date_filters(qs, date_from, date_to):
    if date_from:
        d = parse_date(date_from)
        if d:
            qs = qs.filter(created_at__date__gte=d)
    if date_to:
        d = parse_date(date_to)
        if d:
            qs = qs.filter(created_at__date__lte=d)
    return qs


def _user_search_q(prefix, query):
    """Q для пошуку за користувачем (prefix — напр. user__ або from_user__)."""
    return (
        Q(**{f"{prefix}name__icontains": query})
        | Q(**{f"{prefix}surname__icontains": query})
        | Q(**{f"{prefix}email__icontains": query})
    )


def build_action_logs(query="", action_type="", date_from="", date_to=""):
    """
    Повертає список dict, відсортований за часом (новіші зверху).
    Кожен запис: timestamp, action_type, action_label, auditory, participants, summary.
    """
    query = (query or "").strip()
    action_type = (action_type or "").strip()
    allowed_types = {"", "take", "return", "transfer"}
    if action_type not in allowed_types:
        action_type = ""

    logs = []

    if action_type in ("", "take"):
        take_qs = Key_requests.objects.filter(is_approved=True).select_related(
            "user", "key"
        )
        take_qs = _apply_date_filters(take_qs, date_from, date_to)
        if query:
            take_qs = take_qs.filter(
                Q(key__auditory__icontains=query) | _user_search_q("user__", query)
            )
        for req in take_qs:
            user = req.user
            logs.append(
                {
                    "timestamp": req.created_at,
                    "action_type": "take",
                    "action_label": ACTION_LABELS["take"],
                    "auditory": req.key.auditory,
                    "participants": f"{user.surname} {user.name}",
                    "summary": f"отримав ключ до аудиторії {req.key.auditory}",
                }
            )

    if action_type in ("", "return"):
        return_qs = Key_return_request.objects.filter(is_approved=True).select_related(
            "user", "key"
        )
        return_qs = _apply_date_filters(return_qs, date_from, date_to)
        if query:
            return_qs = return_qs.filter(
                Q(key__auditory__icontains=query) | _user_search_q("user__", query)
            )
        for ret in return_qs:
            user = ret.user
            logs.append(
                {
                    "timestamp": ret.created_at,
                    "action_type": "return",
                    "action_label": ACTION_LABELS["return"],
                    "auditory": ret.key.auditory,
                    "participants": f"{user.surname} {user.name}",
                    "summary": f"повернув ключ від аудиторії {ret.key.auditory}",
                }
            )

    if action_type in ("", "transfer"):
        transfer_qs = Key_transfer.objects.filter(is_approved=True).select_related(
            "from_user", "to_user", "key"
        )
        transfer_qs = _apply_date_filters(transfer_qs, date_from, date_to)
        if query:
            transfer_qs = transfer_qs.filter(
                Q(key__auditory__icontains=query)
                | _user_search_q("from_user__", query)
                | _user_search_q("to_user__", query)
            )
        for tr in transfer_qs:
            f, t = tr.from_user, tr.to_user
            logs.append(
                {
                    "timestamp": tr.created_at,
                    "action_type": "transfer",
                    "action_label": ACTION_LABELS["transfer"],
                    "auditory": tr.key.auditory,
                    "participants": f"{f.surname} {f.name} → {t.surname} {t.name}",
                    "summary": f"передав ключ {tr.key.auditory} іншому користувачу",
                }
            )

    logs.sort(key=lambda row: row["timestamp"], reverse=True)
    return logs


def parse_journal_filters(request):
    """Параметри фільтрів журналу з GET-запиту."""
    query = request.GET.get("q", "").strip()
    action_type = request.GET.get("action", "").strip()
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()
    allowed_types = {"", "take", "return", "transfer"}
    if action_type not in allowed_types:
        action_type = ""
    return query, action_type, date_from, date_to


def journal_filter_query_string(query, action_type, date_from, date_to):
    """Рядок для посилань (пагінація, експорт) без параметра page."""
    params = {}
    if query:
        params["q"] = query
    if action_type:
        params["action"] = action_type
    if date_from:
        params["date_from"] = date_from
    if date_to:
        params["date_to"] = date_to
    return urlencode(params)


def export_action_logs_csv(logs):
    """Відповідь із CSV-файлом журналу (UTF-8 з BOM для Excel)."""
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        ["Дата", "Час", "Тип", "Аудиторія", "Учасники", "Опис"]
    )
    for row in logs:
        local_dt = timezone.localtime(row["timestamp"])
        writer.writerow(
            [
                local_dt.strftime("%d.%m.%Y"),
                local_dt.strftime("%H:%M"),
                row["action_label"],
                row["auditory"],
                row["participants"],
                row["summary"],
            ]
        )
    response = HttpResponse(
        "\ufeff" + buffer.getvalue(),
        content_type="text/csv; charset=utf-8",
    )
    filename = f"journal_{timezone.localdate().isoformat()}.csv"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
