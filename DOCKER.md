# Запуск через Docker Compose

Два сервіси в одному `docker-compose.yml`: **PostgreSQL** і **Django**.

Загальний опис проєкту та локальний запуск без Docker — у [README.md](README.md).

---

## Що потрібно

1. [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Файл `.env` у корені (шаблон: `.env.example`)

---

## Перший запуск

### 1. Змінні середовища

```bash
cp .env.example .env
```

Обов’язково **`SECRET_KEY`**. Генерація:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Опційно для автоматичного bootstrap:

```env
ADMIN_EMAIL=admin@uni.ua
ADMIN_PASSWORD=your-secure-password
ADMIN_NAME=Admin
ADMIN_SURNAME=User
SEED_AUDITORIES=101,102,103,201
```

### 2. Запуск

```bash
docker compose up --build
```

| Що | Адреса |
|----|--------|
| Застосунок | [http://127.0.0.1:8000](http://127.0.0.1:8000) |
| PostgreSQL з хоста (опційно) | `localhost:5433` — логін/БД з `.env` |

Зупинити: `Ctrl+C` або `docker compose down`. Через UI: Docker Desktop → Containers → **Stop**.

---

## Що відбувається при старті

| Сервіс | Роль |
|--------|------|
| **db** | PostgreSQL 16, дані в томі `postgres_data` |
| **web** | `docker/entrypoint.sh` → очікування БД → `migrate` → `ensure_admin` → `seed_auditories` → `runserver` |

Контейнер **web** підключається до БД за іменем **`db`** (внутрішня мережа Docker), не `localhost`.

### `ensure_admin`

Якщо в `.env` задані `ADMIN_EMAIL` / `ADMIN_PASSWORD` і користувача з таким email **ще немає** — створюється staff/superuser. Якщо вже є — без змін.

### `seed_auditories`

Якщо задано `SEED_AUDITORIES=101,102,...` — створюються вільні ключі для цих номерів (без дублікатів).

Якщо bootstrap не використовуєте:

```bash
docker compose exec web python manage.py createsuperuser
```

Додати ключі вручну — через Django shell (див. [README.md](README.md) або `coursework/models.py`).

---

## Корисні команди

```bash
# Фоновий запуск
docker compose up -d --build

# Логи
docker compose logs -f web

# Зупинити (дані БД зберігаються)
docker compose down

# Зупинити і видалити дані БД
docker compose down -v

# Django shell
docker compose exec web python manage.py shell

# Тести
docker compose exec web python manage.py test coursework --settings=config.settings_test -v 2
```

---

## Після запуску

1. Увійти як адмін (`ADMIN_EMAIL` з `.env`) або `createsuperuser`.
2. Користувач реєструється на `/registration/` — **без доступу** до аудиторій.
3. Адмін призначає групи на `/groups/` або винятки на `/users/`.

Покроковий сценарій ручної перевірки: **[docs/testing.md](docs/testing.md)**

---

## Примітка

У контейнері — **сервер розробки** Django (`runserver`), достатній для демонстрації та розробки.
