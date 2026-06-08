# Застосунок для обліку ключів від аудиторій

Вебзастосунок на **Django** для обліку фізичних ключів: запити на видачу та повернення, передача між користувачами, групи доступу, журнал дій та аналітика для адміністратора.

**Стек:** Python 3.12, Django 6, PostgreSQL 16.

> **Рекомендовано запускати через Docker** — не потрібно окремо встановлювати PostgreSQL і налаштовувати Python-оточення. Достатньо [Docker Desktop](https://www.docker.com/products/docker-desktop/) і файлу `.env`. Інструкція: [DOCKER.md](DOCKER.md). Локальний запуск без Docker — нижче, як альтернатива.

---

## Швидкий старт (Docker)

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

Опційно (якщо в `.env` задані `ADMIN_*`):

```bash
python manage.py ensure_admin
```

### Аудиторії (без Docker)

**Через `.env` і management-команду** — додайте в `.env`:

```env
SEED_AUDITORIES=101,102,103,201
```

Потім:

```bash
python manage.py seed_auditories
```

Створюються вільні ключі для номерів, яких ще немає в БД. Повторний запуск дублікатів не створює.

**Вручну через shell:**

```bash
python manage.py shell
```

```python
from coursework.models import Key

Key.objects.create(auditory="101")
Key.objects.bulk_create([
    Key(auditory="201"),
    Key(auditory="202"),
])
```

Вийти: `exit()` або `Ctrl+D`.

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
