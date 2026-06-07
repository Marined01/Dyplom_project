# Структура проєкту

```
Coursework_/
├── config/                 # Налаштування Django
│   ├── settings.py         # Основні settings (PostgreSQL, AUTH_USER_MODEL)
│   ├── settings_test.py    # Тести: SQLite in-memory
│   ├── urls.py             # Маршрути застосунку
│   └── wsgi.py
├── coursework/             # Основний Django-додаток
│   ├── models.py           # User, Key, AccessGroup, запити, журнал
│   ├── views.py            # HTTP-обробники сторінок
│   ├── access.py           # Перевірки доступу до ключів
│   ├── admin_requests.py   # Черга запитів адміна (видача / повернення)
│   ├── dashboard.py        # Дані для аналітичної панелі
│   ├── journal.py          # Журнал підтверджених операцій
│   ├── users_admin.py      # Список і редагування користувачів
│   ├── groups_admin.py     # CRUD груп доступу
│   ├── key_metrics.py      # Метрики для dashboard
│   ├── migrations/         # Міграції БД
│   ├── management/commands/
│   │   ├── ensure_admin.py # Створення адміна з ADMIN_* (.env)
│   │   └── seed_auditories.py  # Початкові ключі з SEED_AUDITORIES
│   └── tests/              # Модульні тести (10)
├── templates/              # HTML-шаблони (Django templates)
├── static/                 # CSS (app.css), JS (nav.js, theme.js)
├── docker/
│   └── entrypoint.sh       # migrate → ensure_admin → seed → runserver
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── requirements.txt
├── .env.example
├── README.md               # Швидкий старт
├── DOCKER.md               # Docker Compose
└── docs/                   # Ця документація
```

---

## Модулі `coursework/`

| Модуль | Призначення |
|--------|-------------|
| `models.py` | Сутності БД: користувачі, ключі, групи, запити на видачу/повернення/передачу, записи журналу |
| `access.py` | `user_has_any_access`, `user_can_access_key`, `keys_queryset_for_user` |
| `views.py` | Сторінки для користувача та адміна |
| `admin_requests.py` | Активна черга запитів на видачу та повернення (15 хв) |
| `journal.py` | Фільтрація та експорт журналу дій |
| `dashboard.py` | Зведення для `/dashboard/` |

---

## Основні моделі

| Модель | Опис |
|--------|------|
| `User` | Email-логін, `is_staff`, M2M `access_groups`, M2M `allowed_keys` (винятки) |
| `AccessGroup` | Назва групи; M2M до користувачів і ключів |
| `Key` | Аудиторія, статус (`free` / `taken` / `pending`), тримач |
| `Key_requests` | Запит на видачу (очікує підтвердження адміна) |
| `Key_return_request` | Запит на повернення (очікує підтвердження адміна)|
| `Key_transfer` | Запит на передачу (підтверджує отримувач) |

Журнал дій (`/action_view/`) будується з **підтверджених** записів цих моделей (`journal.py`), окремої таблиці журналу немає.

Логіка ключів (ліміт 4 ключі, зміна статусу) — у методах моделі `Key` у `models.py`.
