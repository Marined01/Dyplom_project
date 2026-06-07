# Тестування

## Автоматичні тести

10 модульних тестів у `coursework/tests/` (SQLite in-memory через `config/settings_test.py`).

```bash
python manage.py test coursework --settings=config.settings_test -v 2
```

У Docker:

```bash
docker compose exec web python manage.py test coursework --settings=config.settings_test -v 2
```

| Файл | Що перевіряє |
|------|--------------|
| `test_access.py` | staff, новий користувач без доступу, група відкриває доступ |
| `test_key_model.py` | take/put, ліміт 4 ключі |
| `test_views.py` | login required, блок видачі без доступу, free-keys фільтр |

---

## Ручна перевірка

Потрібні **два сеанси браузера** одночасно (користувач + адміністратор):

| Вікно | Роль |
|-------|------|
| Браузер 1 (або інкognito) | Адміністратор — `ADMIN_EMAIL` з `.env` |
| Браузер 2 | Звичайний користувач — реєстрація на `/registration/` |

---

### Приклад `.env` для перевірки

```env
POSTGRES_DB=coursework_db
POSTGRES_USER=coursework
POSTGRES_PASSWORD=demo_db_pass

SECRET_KEY=вставте-згенерований-ключ
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

ADMIN_EMAIL=admin@uni.ua
ADMIN_PASSWORD=Admin12345
ADMIN_NAME=Admin
ADMIN_SURNAME=User

SEED_AUDITORIES=101,102,103,201
```

Після `docker compose up` створяться адмін і вільні аудиторії з цього списку.

---

### Сценарій (покроково)

#### 1. Адмін — перше вікно

1. [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/)
2. Email: `admin@uni.ua`, пароль: `Admin12345`
3. У меню — розділи адміна (запити, користувачі, групи)

#### 2. Користувач — друге вікно

1. [http://127.0.0.1:8000/registration/](http://127.0.0.1:8000/registration/)
2. Наприклад: `student@uni.ua`, пароль ≥ 8 символів
3. «Вільні аудиторії» порожні — очікувано

#### 3. Адмін — група доступу

1. [http://127.0.0.1:8000/groups/](http://127.0.0.1:8000/groups/) → **Нова група**
2. Аудиторії `101`, `102`, `103` + користувач `student@uni.ua`
3. Зберегти

#### 4. Користувач — запит на ключ

1. [http://127.0.0.1:8000/free-keys/](http://127.0.0.1:8000/free-keys/) — з’являться доступні
2. **Подати запит** для `101`
3. На `/keys/` статус «Очікує»

#### 5. Адмін — підтвердження видачі

1. [http://127.0.0.1:8000/requests/](http://127.0.0.1:8000/requests/) → **Підтвердити**
2. На `/keys/` — «Зайнята», тримач — студент

#### 6. Повернення

1. Користувач: головна → **Запит на повернення**
2. Адмін: `/requests/` → **Підтвердити**
3. Аудиторія знову «Вільна»

#### 7. Передача

1. Користувач A тримає ключ; B має доступ (група або виняток)
2. A: **Передати ключ** → ім’я та прізвище B
3. B: [http://127.0.0.1:8000/transfers/](http://127.0.0.1:8000/transfers/) → **Підтвердити**

#### 8. Журнал і аналітика

Адмін: `/dashboard/`, `/action_view/`.

---

### Зупинка

- `Ctrl+C` або Docker Desktop → **Stop**
- Повний скидання БД: `docker compose down -v`

---

## Мобільна верстка

Перевірка через інструменти розробника браузера (`F12` → режим пристрою).
