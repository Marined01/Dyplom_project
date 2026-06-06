# Запуск через Docker Compose

Один файл описує **два сервіси**: PostgreSQL і Django. Команда `docker compose up` піднімає обидва.

Детальніше про локальний запуск без Docker, сторінки застосунку та змінні середовища — у [README.md](README.md).

---

## Що потрібно

1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) (macOS / Windows / Linux)
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
| **web** | `docker/entrypoint.sh`: чекає БД → `migrate` → `runserver` |

Контейнер **web** з’єднується з БД за іменем **`db`** (внутрішня мережа Docker), не `localhost`.

---

## Після першого запуску

### Адміністратор

У БД ще немає користувачів. У **новому** терміналі (контейнери мають працювати):

```bash
docker compose exec web python manage.py createsuperuser
```

Уведіть email, ім’я, прізвище та пароль. Користувач отримає `is_staff` і зможе відкрити чергу запитів, дашборд, журнал, `/users/`, `/groups/`.

### Аудиторії (ключі)

У застосунку немає окремої сторінки «додати аудиторію». Найпростіше створити ключі **через Django shell** (без `/admin/`):

```bash
docker compose exec web python manage.py shell
```

У консолі Python:

```python
from coursework.models import Key

Key.objects.create(auditory="101")
Key.objects.create(auditory="102")

# або кілька одразу:
Key.objects.bulk_create([
    Key(auditory="201"),
    Key(auditory="202"),
    Key(auditory="203"),
])

# перевірити:
list(Key.objects.values_list("auditory", flat=True))
```

Вийти з shell: `exit()` або `Ctrl+D`.

### Доступ користувачів

Нові користувачі реєструються на `/registration/` **без доступу до аудиторій**. Після реєстрації система підказує звернутися до адміністратора.

Адмін призначає доступ:

- **Групи доступу** — [http://127.0.0.1:8000/groups/](http://127.0.0.1:8000/groups/)
- **Групи + додаткові аудиторії** для конкретного користувача — `/users/` → редагування

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

У контейнері використовується **сервер розробки** Django (`runserver`) — достатньо для демонстрації та розробки, не для production.
