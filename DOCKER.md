# Запуск через Docker Compose

Один файл описує **два сервіси**: база PostgreSQL і Django. Команда `docker compose up` піднімає обидва.

## Що потрібно на комп’ютері

1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) (macOS / Windows / Linux)
2. У терміналі з папки проєкту:

```bash
cp .env.example .env
docker compose up --build
```

3. Відкрийте в браузері: **http://127.0.0.1:8000/**

Зупинити: `Ctrl+C`, або в іншому терміналі `docker compose down`.

---

## Що відбувається під капотом

| Сервіс | Роль |
|--------|------|
| **db** | PostgreSQL 16, дані в томі `postgres_data` |
| **web** | Django: чекає БД → `migrate` → `runserver` |

Сайт звертається до БД за ім’ям **`db`** (внутрішня мережа Docker), не `localhost`.

---

## Перший запуск: адміністратор

У БД ще немає користувачів. Створіть staff (у **новому** терміналі, поки контейнери працюють):

```bash
docker compose exec web python manage.py createsuperuser
```

Далі увійдіть на сайт з цим email і паролем.

---

## Корисні команди

```bash
# Запуск у фоні
docker compose up -d --build

# Логи
docker compose logs -f web

# Зупинити і прибрати контейнери (дані БД залишаться у volume)
docker compose down

# Зупинити і видалити дані БД
docker compose down -v

# Shell у контейнері Django
docker compose exec web python manage.py shell
```

---
## Локальна розробка без Docker

Як раніше: venv + Postgres на `localhost`. У `config/settings.py` залишені значення за замовчуванням для вашої локальної БД, якщо змінні середовища не задані.
