# Как добавить новое приложение в проект

Этот проект использует multi-DB архитектуру (как в Bastion) для масштабирования.
Каждое приложение использует свою базу данных для изоляции данных.

## Шаг 1: Создать приложение

```bash
cd c:/develop/mikesdemos/opencbbl
python manage.py startapp myapp
```

## Шаг 2: Добавить Router в `opencbbl/routers.py`

Создайте класс Router для вашего приложения:

```python
class MyappRouter:
    """Роутер для приложения myapp"""
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'myapp':
            return 'myapp_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'myapp':
            return 'myapp_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'myapp' or obj2._meta.app_label == 'myapp':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'myapp':
            return db == 'myapp_db'
        return None
```

## Шаг 3: Добавить Router в `DATABASE_ROUTERS` в `opencbbl/settings.py`

```python
DATABASE_ROUTERS = [
    'opencbbl.routers.AuthRouter',
    'opencbbl.routers.OrganizationsRouter',
    'opencbbl.routers.ApiRouter',
    'opencbbl.routers.AccountsRouter',
    'opencbbl.routers.InventoryRouter',
    'opencbbl.routers.BuildsRouter',
    'opencbbl.routers.DashboardRouter',
    'opencbbl.routers.MyappRouter',  # <-- добавить сюда
]
```

## Шаг 4: Добавить базу данных в `opencbbl/settings.py`

Для PostgreSQL:
```python
'myapp_db': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': os.getenv('MYAPP_DB_NAME', 'myapp_data'),
    'USER': os.getenv('DB_USER', 'opencbbl'),
    'PASSWORD': os.getenv('DB_PASSWORD', ''),
    'HOST': os.getenv('DB_HOST', 'localhost'),
    'PORT': os.getenv('DB_PORT', '5432'),
},
```

Для SQLite (разработка):
```python
'myapp_db': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'myapp_db.sqlite3',
},
```

## Шаг 5: Добавить приложение в `INSTALLED_APPS` в `opencbbl/settings.py`

```python
INSTALLED_APPS = [
    # ... другие приложения
    'myapp',
]
```

## Шаг 6: Добавить URL префикс в `opencbbl/urls.py`

```python
urlpatterns = [
    # ... другие URL
    path('myapp/', include('myapp.urls')),
]
```

## Шаг 7: Создать миграции и применить

```bash
python manage.py makemigrations myapp
python manage.py migrate myapp --database=myapp_db
```

## Шаг 8: Создать `urls.py` в приложении

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]
```

## Шаг 9: Добавить переменные окружения в `.env` (если нужно)

```env
MYAPP_DB_NAME=myapp_data
```

## Примеры существующих приложений

- **opencbbl**: `/black-list-cbrf/` → БД `opencbbl_db`
- **pcmanager**: `/pcmanager/` → БД `pcmanager_db`

## Структура проекта

```
opencbbl/
├── opencbbl/
│   ├── settings.py          # Конфигурация
│   ├── urls.py              # Главный URL конфиг
│   └── routers.py           # Database routers
├── organizations/           # Приложение 1 (opencbbl_db)
├── api/                     # Приложение 2 (opencbbl_db)
├── apps/                    # Папка для приложений
│   ├── accounts/            # Приложение 3 (pcmanager_db)
│   ├── inventory/           # Приложение 4 (pcmanager_db)
│   ├── builds/              # Приложение 5 (pcmanager_db)
│   └── dashboard/           # Приложение 6 (pcmanager_db)
└── myapp/                   # Новое приложение (myapp_db)
```

## Важные моменты

1. **Изоляция БД**: Каждое приложение использует свою БД через router
2. **URL префиксы**: Избегайте конфликтов URL с префиксами
3. **Миграции**: Применяйте миграции с `--database=<db_name>`
4. **Шаблоны**: Используйте общую папку `templates/` или создайте `myapp/templates/myapp/`
5. **Статика**: Используйте общую папку `static/` или создайте `myapp/static/myapp/`
