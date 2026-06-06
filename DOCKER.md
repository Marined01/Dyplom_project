# Запуск через Docker Compose

Один файл описує **два сервіси**: PostgreSQL і Django. 

Детальніше про локальний запуск без Docker, перевірку застосунку та змінні середовища — у [README.md](README.md).

---

## Що потрібно

1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) 
2. Файл `.env` у корені проєкту (див. нижче)

---

## Перший запуск

### 1. Змінні середовища

```bash
cp .env.example .env
```

Обов’язково вкажіть **`SECRET_KEY`** (без нього Django не запуститься). Покроково: генерація командою, приклад `.env` — у [README.md](README.md#змінні-середовища-env).

### 2. Запуск

```bash
docker compose up --build
```

Після старту:

- застосунок: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- PostgreSQL з **хост-машини** (опційно): `localhost:5433` — логін/БД з `.env`

Зупинити:

- у терміналі: `Ctrl+C` (якщо `up` без `-d`) або `docker compose down`;
- **через UI:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) → Containers → проєкт `coursework` → **Stop** (або зупинити окремо `web` і `db`).

---

## Що відбувається під капотом

| Сервіс | Роль |
|--------|------|
| **db** | PostgreSQL 16, дані в томі `postgres_data` |
| **web** | `docker/entrypoint.sh`: чекає БД → `migrate` → `ensure_admin` → `seed_auditories` → `runserver` |

Контейнер **web** з’єднується з БД за іменем **`db`** (внутрішня мережа Docker), не `localhost`.

---

## Після першого запуску

### Адміністратор

**Автоматично (Docker):** додайте в `.env`:

```env
ADMIN_EMAIL=admin@uni.ua
ADMIN_PASSWORD=your-secure-password
ADMIN_NAME=Admin
ADMIN_SURNAME=User
```

Після `docker compose up` entrypoint виконає `migrate`, потім `ensure_admin`. Якщо користувача з таким email **ще немає** — створить staff/superuser. Якщо **вже є** — нічого не змінює.

**Аудиторії (опційно):** у `.env` можна додати:

```env
SEED_AUDITORIES=101,102,103,201
```

При старті створяться вільні ключі для цих номерів, якщо їх ще немає в БД.

**Вручну** (якщо `ADMIN_*` не задані або потрібен інший обліковий запис):

```bash
docker compose exec web python manage.py createsuperuser
```

### Аудиторії (ключі)

Якщо `SEED_AUDITORIES` не задано — ключі можна додати **через Django shell**:

```bash
docker compose exec web python manage.py shell
```

```python
from coursework.models import Key

Key.objects.create(auditory="101")
Key.objects.bulk_create([
    Key(auditory="201"),
    Key(auditory="202"),
])
```

Вийти з shell: `exit()` або `Ctrl+D`.

### Доступ користувачів

Нові користувачі реєструються на `/registration/` **без доступу до аудиторій**. Адміністратор призначає доступ на `/groups/` та `/users/`. Як перевірити сценарії вручну — у [README.md](README.md#перевірка-застосунку).

---

## Корисні команди

```bash
# Запуск у фоні
docker compose up -d --build

# Логи
docker compose logs -f web

# Зупинити контейнери (дані БД у volume залишаться)
docker compose down

# Те саме через Docker Desktop: Containers → coursework → Stop

# Зупинити і видалити дані БД
docker compose down -v

# Django shell
docker compose exec web python manage.py shell

# Тести (SQLite in-memory, робоча Postgres не чіпається)
docker compose exec web python manage.py test coursework --settings=config.settings_test -v 2
```

---

## Локальна розробка без Docker

Python 3.12+, PostgreSQL на `localhost` — покроково в [README.md](README.md).

---

## Примітка

У контейнері використовується **сервер розробки** Django (`runserver`) — достатньо для демонстрації та розробки.
