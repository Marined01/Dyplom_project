# ЗАСТОСУНОК ДЛЯ ОБЛІКУ КЛЮЧІВ ВІД АУДИТОРІЙ НАВЧАЛЬНОГО ЗАКЛАДУ

Вебзастосунок на **Django** для обліку фізичних ключів від навчальних аудиторій: запити на видачу та повернення, передача між користувачами, дворівневе розмежування доступу, журнал дій та аналітика для адміністратора.

**Стек:** Python 3.12, Django 6, PostgreSQL 16.

---

## Зміст

- [Швидкий старт (Docker)](#швидкий-старт-docker)
- [Локальний запуск](#локальний-запуск)
- [Після першого запуску](#після-першого-запуску)
- [Обмеження доступу](#обмеження-доступу)
- [Основні сторінки](#основні-сторінки)
- [Тести](#тести)
- [Мобільна версія та доступ з телефона](#мобільна-версія-та-доступ-з-телефона)
- [Змінні середовища](#змінні-середовища-env)
- [Структура проєкту](#структура-проєкту)

---

## Швидкий старт (Docker)

1. `cp .env.example .env` — заповніть `.env`, зокрема **`SECRET_KEY`** ([інструкція](#змінні-середовища-env)).
2. `docker compose up --build`
3. Відкрийте [http://127.0.0.1:8000](http://127.0.0.1:8000)

Детальні інструкції: **[DOCKER.md](DOCKER.md)**.

---

## Локальний запуск

Потрібні: **Python 3.12+**, **PostgreSQL 16+**.

### 1. Змінні середовища

Скопіюйте шаблон і заповніть `.env` — покроково в розділі **[Змінні середовища (`.env`)](#змінні-середовища-env)** (генерація `SECRET_KEY`, приклад для локального запуску).

```bash
cp .env.example .env
```

### 2. PostgreSQL

```sql
CREATE USER coursework WITH PASSWORD 'your-password-here';
CREATE DATABASE coursework_db OWNER coursework;
GRANT ALL PRIVILEGES ON DATABASE coursework_db TO coursework;
```

(Логін, пароль і ім’я БД — як у `.env`.)

### 3. Віртуальне середовище

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Міграції та сервер

```bash
python manage.py migrate
python manage.py runserver
```

Сайт: [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## Після першого запуску

### Адміністратор

Реєстрація на `/registration/` створює **звичайного** користувача. Перший адмін — через:

```bash
python manage.py createsuperuser
```

У Docker:

```bash
docker compose exec web python manage.py createsuperuser
```

Після входу для адміністратора доступні черга запитів, дашборд, журнал, та інші розширені можливості.

### Аудиторії (ключі)

Окремої сторінки «додати аудиторію» немає. Створіть ключі через **Django shell**:

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

У Docker: `docker compose exec web python manage.py shell` — детальніше в [DOCKER.md](DOCKER.md).

### Доступ користувачів

Новий користувач **не має доступу** до аудиторій, доки адмін не призначить його. Після реєстрації з’являється підказка звернутися до адміністратора.

Призначення доступу:

- **Групи доступу** 
- **Групи + окремі аудиторії** для одного користувача 

---

## Обмеження доступу

| Хто                                       | Що бачить / може робити                                   |
|-------------------------------------------|-----------------------------------------------------------|
| **Без груп і без allowlist**              | Немає доступу до нових ключів; «Вільні аудиторії» порожні |
| **Група доступу**                         | Аудиторії з групи                                         |
| **Додаткові аудиторії (не цілою групою)** | Додаткові аудиторії поверх груп                           |
| **Адміністратор (`is_staff`)**            | Повний доступ                                             |
| **Ключі та пошук**                        | Усі аудиторії видно; лише доступні дії                    |
| **Вільні аудиторії**                      | Лише **вільні** аудиторії з доступних користувачу         |
| **Передача**                              | Отримувач теж повинен мати доступ до аудиторії            |

---

## Основні сторінки

| URL | Опис |
|-----|------|
| `/` | Головна — ключі на руках у користувача |
| `/registration/` | Реєстрація |
| `/login/` | Вхід |
| `/free-keys/` | Вільні аудиторії (з урахуванням доступу) |
| `/keys/` | Усі ключі, пошук і фільтри |
| `/transfers/` | Вхідні запити на передачу |
| `/requests/` | Черга запитів на видачу/повернення *(адмін)* |
| `/dashboard/` | Дашборд *(адмін)* |
| `/action_view/` | Журнал дій *(адмін)* |
| `/users/` | Користувачі *(адмін)* |
| `/groups/` | Групи доступу *(адмін)* |
| `/admin/` | Стандартна адмінка Django (Keys, User) |

---

## Тести

10 автоматичних перевірок (доступ, правила ключів, основні сторінки). Запуск на **тимчасовій SQLite** — робоча PostgreSQL не змінюється.

```bash
python manage.py test coursework --settings=config.settings_test -v 2
```

`-v 2` — виводить кожен тест окремим рядком.

У Docker:

```bash
docker compose exec web python manage.py test coursework --settings=config.settings_test -v 2
```

---

## Мобільна версія та доступ з телефона

### Перевірка в браузері (основний спосіб)

Адаптивну верстку зручно перевіряти **в інструментах розробника браузера** — без реального телефона:

- **Chrome / Edge:** `F12` → іконка «Пристрій» / **Toggle device toolbar** — вікно стає вужчим, можна обрати модель телефона зі списку.

Так перевіряли мобільне меню, таблиці та форми на різній ширині екрана.

---

## Змінні середовища (`.env`)

Файл `.env` лежить у **корені проєкту** (поруч із `manage.py`). Його **не комітять** у git — у репозиторії лише шаблон `.env.example`.

### Крок 1. Створити файл

```bash
cp .env.example .env
```

### Крок 2. Згенерувати `SECRET_KEY`

Django **не запуститься**, якщо `SECRET_KEY` порожній або залишився `your-secret-key-here`.

Після `pip install -r requirements.txt` (або в активованому `venv`):

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

У терміналі з’явиться довгий рядок, наприклад:

```
django-insecure-a1b2c3d4e5f6...
```

Скопіюйте його **цілком** і вставте в `.env`:

```env
SECRET_KEY=django-insecure-a1b2c3d4e5f6...
```

Без лапок, без пробілів навколо `=`.

### Крок 3. Заповнити решту полів

**Локальний запуск** (PostgreSQL на `localhost`):

```env
POSTGRES_DB=coursework_db
POSTGRES_USER=coursework
POSTGRES_PASSWORD=your-password-here

DB_HOST=localhost
DB_PORT=5432

SECRET_KEY=<рядок з кроку 2>

DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

`POSTGRES_PASSWORD` має **збігатися** з паролем користувача PostgreSQL, якого ви створили в SQL (див. [локальний запуск](#локальний-запуск)).

**Docker** — ті самі змінні; `DB_HOST=db` у контейнері `web` підставляє `docker-compose.yml` автоматично. У `.env` для Docker достатньо значень як у `.env.example`, головне — **`SECRET_KEY`** і **`POSTGRES_PASSWORD`**.

### Що означає кожна змінна

| Змінна | Обов’язково | Опис |
|--------|------------|------|
| `SECRET_KEY` | **Так** | Секрет Django (сесії, підписи). Генерується один раз, не публікується |
| `POSTGRES_DB` | Так | Ім’я бази, за замовч. `coursework_db` |
| `POSTGRES_USER` | Так | Користувач PostgreSQL |
| `POSTGRES_PASSWORD` | Так | Пароль PostgreSQL |
| `DB_HOST` | Так локально | `localhost` без Docker; у контейнері — `db` |
| `DB_PORT` | Так | `5432` |
| `DEBUG` | Ні | `True` — режим розробки |
| `ALLOWED_HOSTS` | Ні | З яких адрес можна відкривати сайт (через кому). Для телефона в Wi‑Fi додайте IP комп’ютера |

### Перевірка

Після збереження `.env`:

```bash
python manage.py migrate
```

Якщо помилка `SECRET_KEY is not set` або `POSTGRES_USER and POSTGRES_PASSWORD must be set` — перевірте, що файл називається саме `.env`, лежить у корені проєкту, і всі обов’язкові рядки заповнені.

---

## Структура проєкту

```
config/              # settings, urls, settings_test (для тестів)
coursework/          # моделі, views, access.py, tests/
templates/           # HTML-шаблони
static/              # CSS, JavaScript
docker/              # entrypoint для контейнера web
docker-compose.yml
Dockerfile
DOCKER.md            # Docker: запуск, shell, зупинка через UI
manage.py
```

---

## Примітка

У розробці використовується **сервер Django `runserver`** — достатньо для демонстрації.