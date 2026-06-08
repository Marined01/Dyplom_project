# URL-маршрути

Базова адреса локально: [http://127.0.0.1:8000](http://127.0.0.1:8000)

Маршрути визначені в `config/urls.py`.

---

## Авторизація та профіль

| URL | Name | Опис |
|-----|------|------|
| `/login/` | `login` | Вхід |
| `/registration/` | `registration` | Реєстрація |
| `/logout/` | `logout` | Вихід |
| `/profile/` | `profile` | Профіль користувача |
| `/edit-profile/` | `profile_edit` | Редагування профілю |

---

## Користувач

| URL | Name | Опис |
|-----|------|------|
| `/` | `home` | Головна — ключі в користуванні |
| `/free-keys/` | `free_keys` | Вільні аудиторії (лише з доступом) |
| `/keys/` | `key_list` | Усі ключі; дії — за правилами доступу |
| `/keys/<id>/take/` | `take_key` | Запит на видачу |
| `/keys/<id>/put/` | `put_key` | Запит на повернення |
| `/request-key/<id>/` | `take_key_request` | POST: створити запит на видачу |
| `/request-put-key/<id>` | `put_key_request` | POST: створити запит на повернення |
| `/transfer/<id>/` | `transfer_key` | Форма передачі ключа |
| `/transfers/` | `incoming_transfers` | Вхідні запити на передачу |
| `/approve_transfer/<id>/` | `approve_transfer` | Підтвердити передачу |
| `/reject_transfer/<id>/` | `reject_transfer` | Відхилити передачу |

---

## Адміністратор (`is_staff`)

| URL | Name | Опис |
|-----|------|------|
| `/requests/` | `admin_requests` | Черга: видача + повернення |
| `/dashboard/` | `dashboard` | Аналітика |
| `/action_view/` | `action_view` | Журнал дій |
| `/action_view/export/` | `action_view_export` | Експорт журналу (CSV) |
| `/users/` | `admin_user_list` | Користувачі |
| `/users/<id>/edit/` | `admin_user_edit` | Редагування користувача, винятки |
| `/groups/` | `admin_access_group_list` | Групи доступу |
| `/groups/new/` | `admin_access_group_create` | Нова група |
| `/groups/<id>/edit/` | `admin_access_group_edit` | Редагування групи |

---

## Підтвердження запитів (адмін)

| URL | Name | Опис |
|-----|------|------|
| `/key-requests/approve/<id>/` | `approve_take_request` | Підтвердити видачу |
| `/key-requests/reject/<id>/` | `reject_key_request` | Відхилити видачу |
| `/return-request/approve/<id>/` | `approve_put_request` | Підтвердити повернення |
| `/return-request/reject/<id>/` | `reject_put_request` | Відхилити повернення |

> **Примітка:** передачі ключів адмін **не** підтверджує — лише отримувач на `/transfers/`.
