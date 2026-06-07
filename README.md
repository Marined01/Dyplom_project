# Застосунок для обліку ключів від аудиторій

Вебзастосунок на **Django** для обліку фізичних ключів: запити на видачу та повернення, передача між користувачами, групи доступу, журнал дій та аналітика для адміністратора.

**Стек:** Python 3.12, Django 6, PostgreSQL 16.

---

## Швидкий старт (Docker)

Рекомендований спосіб запуску.

```bash
cp .env.example .env
# Вкажіть SECRET_KEY (див. нижче)

docker compose up --build
```

Сайт: [http://127.0.0.1:8000](http://127.0.0.1:8000)

Покрокова інструкція з Docker: **[DOCKER.md](DOCKER.md)**

---

## Локальний запуск (без Docker)

Потрібні **Python 3.12+** і **PostgreSQL 16+**.

```bash
cp .env.example .env
# DB_HOST=localhost

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Опційно (якщо в `.env` задані `ADMIN_*` і `SEED_AUDITORIES`):

```bash
python manage.py ensure_admin
python manage.py seed_auditories
```

---

## `SECRET_KEY`

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Вставте результат у `.env`: `SECRET_KEY=...` (без лапок). Повний перелік змінних — у `.env.example`.

---

## Тести

```bash
python manage.py test coursework --settings=config.settings_test -v 2
```

Ручна перевірка (два браузери, сценарії): **[docs/testing.md](docs/testing.md)**

---

## Документація

| Файл | Зміст |
|------|--------|
| [docs/](docs/README.md) | Структура проєкту, URL, доступ, тестування |
| [DOCKER.md](DOCKER.md) | Docker Compose, entrypoint, команди |

---

## Примітка

У проєкті використовується сервер розробки Django (`runserver`) — достатньо для демонстрації та перевірки роботи.
