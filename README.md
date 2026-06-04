# Облік ключів аудиторій

Вебзастосунок на **Django** для обліку фізичних ключів до навчальних аудиторій: запити на видачу/повернення, передача між користувачами, адміністративна черга, дашборд і журнал дій.

**Стек:** Python 3.12, Django 6, PostgreSQL 16.

---

## Перед запуском

1. Склонуйте репозиторій і перейдіть у папку проєкту.
2. Скопіюйте файл змінних середовища:

```bash
cp .env.example .env
```

3. Відредагуйте `.env`:
   - `SECRET_KEY` — обов'язково (можна згенерувати командою нижче);
   - `POSTGRES_PASSWORD` — надійний пароль для БД.

Згенерувати `SECRET_KEY`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Варіант 1: Docker (рекомендовано)

Потрібні: [Docker](https://docs.docker.com/get-docker/) і [Docker Compose](https://docs.docker.com/compose/).

Запуск:

```bash
docker compose up --build
```

Після старту:

- застосунок: [http://localhost:8000](http://localhost:8000);
- PostgreSQL з хоста (опційно): `localhost:5433` (користувач/БД з `.env`).

Compose піднімає два контейнери:

- **db** — PostgreSQL;
- **web** — Django (очікує БД, виконує `migrate`, запускає `runserver`).

Зупинити:

```bash
docker compose down
```

Повністю видалити дані БД (обережно):

```bash
docker compose down -v
```

---

## Варіант 2: Локально (без Docker)

Потрібні: **Python 3.12+**, **PostgreSQL 16+** (або сумісна версія).

### 1. PostgreSQL

Створіть базу та користувача (значення мають збігатися з `.env`):

```sql
CREATE USER coursework WITH PASSWORD 'your-password-here';
CREATE DATABASE coursework_db OWNER coursework;
GRANT ALL PRIVILEGES ON DATABASE coursework_db TO coursework;
```

У `.env` для локального запуску:

```env
DB_HOST=localhost
DB_PORT=5432
```

### 2. Віртуальне середовище та залежності

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Міграції та сервер

```bash
python manage.py migrate
python manage.py runserver
```

Відкрийте [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## Перший адміністратор

Користувачі реєструються через `/registration/`. Щоб надати права адміністратора (`is_staff`):

```bash
python manage.py createsuperuser
```

Уведіть **email**, **ім'я**, **прізвище** та пароль. Після входу з `is_staff=True` доступні черга запитів, дашборд, журнал і керування користувачами.

У Docker:

```bash
docker compose exec web python manage.py createsuperuser
```

---

## Доступ з телефона (локальна мережа)

1. Дізнайтеся IP комп'ютера в Wi‑Fi (наприклад, `192.168.1.42`).
2. Додайте IP у `.env`:

```env
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,192.168.1.42
```

3. Запустіть сервер на всіх інтерфейсах:

```bash
python manage.py runserver 0.0.0.0:8000
```

4. На телефоні відкрийте `http://192.168.1.42:8000` (комп'ютер і телефон — в одній мережі).

---

## Основні сторінки

| URL | Опис |
|-----|------|
| `/` | Головна — ключі користувача |
| `/registration/` | Реєстрація |
| `/login/` | Вхід |
| `/free-keys/` | Вільні аудиторії |
| `/keys/` | Список ключів і пошук |
| `/transfers/` | Вхідні запити на передачу |
| `/requests/` | Черга запитів (лише адмін) |
| `/dashboard/` | Дашборд (лише адмін) |
| `/action_view/` | Журнал дій (лише адмін) |
| `/users/` | Користувачі (лише адмін) |
| `/admin/` | Стандартна адмін-панель Django |

---

## Змінні середовища (`.env`)

| Змінна | Опис |
|--------|------|
| `SECRET_KEY` | Секретний ключ Django (обов'язково) |
| `POSTGRES_DB` | Ім'я бази даних |
| `POSTGRES_USER` | Користувач PostgreSQL |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL |
| `DB_HOST` | `localhost` локально; `db` у Docker Compose |
| `DB_PORT` | `5432` |
| `DEBUG` | `True` для розробки |
| `ALLOWED_HOSTS` | Дозволені хости через кому |

---

## Структура проєкту

```
config/          # налаштування Django (settings, urls)
coursework/      # моделі, views, бізнес-логіка
templates/       # HTML-шаблони
static/          # CSS, JavaScript
docker/          # entrypoint для контейнера web
docker-compose.yml
Dockerfile
manage.py
```

---

## Примітка

У Docker використовується **сервер розробки Django** (`runserver`) — достатньо для демонстрації та розробки.
