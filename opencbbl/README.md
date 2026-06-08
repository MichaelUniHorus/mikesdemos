# MikesDemos - Multi-App Django Project

Единый Django проект для демо-приложений с multi-DB архитектурой для масштабирования.

## Приложения

- **OpenCBBL** - Карта компаний из списка ЦБ РФ (черный список)
- **PC Manager** - Управление компьютерами и сборками
  - Inventory - Складской учет комплектующих
  - Builds - Сборка и конфигурация ПК
  - Dashboard - Главная панель управления

## Архитектура

Проект использует multi-DB архитектуру (как в Bastion):
- Каждое приложение использует свою базу данных
- Database routers для маршрутизации запросов
- URL префиксы для изоляции приложений
- Простое масштабирование - см. `ADD_NEW_APP.md`

## Технологический стек

- **Backend**: Django 4.2 + Django REST Framework
- **Frontend**: HTML + JavaScript + Bootstrap 5
- **Database**: SQLite (разработка) / PostgreSQL (production)
- **Server**: Gunicorn + Nginx
- **API**: ЦБ РФ Warning List API

## Установка и запуск (разработка)

### 1. Клонирование и установка зависимостей

```bash
cd C:\develop\mikesdemos\opencbbl
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Настройка окружения

```bash
copy .env.example .env
```

Отредактируйте `.env` при необходимости.

### 3. Создание баз данных и миграции

```bash
python manage.py migrate --database=default
python manage.py migrate --database=opencbbl_db
python manage.py migrate --database=pcmanager_db
```

### 4. Создание суперпользователя

```bash
python manage.py createsuperuser
```

### 5. Запуск сервера

```bash
python manage.py runserver
```

Приложение будет доступно по адресу: http://localhost:8000

## Доступные URL

- `/` - Главное меню со ссылками на все приложения
- `/black-list-cbrf/` - Черный список ЦБ РФ
- `/black-list-cbrf/api/` - REST API для черного списка
- `/pcmanager/` - PC Manager дашборд
- `/pcmanager/inventory/` - Склад
- `/pcmanager/builds/` - Сборки ПК
- `/admin/` - Админка Django

## API endpoints (OpenCBBL)

- `GET /black-list-cbrf/api/regions/` - список субъектов РФ
- `GET /black-list-cbrf/api/themas/` - список признаков нелегальной деятельности
- `GET /black-list-cbrf/api/organizations/` - список организаций (с фильтрами)
- `GET /black-list-cbrf/api/locations/` - точки для карты

## Структура проекта

```
opencbbl/
├── opencbbl/              # Основные настройки Django
│   ├── settings.py        # Конфигурация
│   ├── urls.py           # Главный URL конфиг
│   ├── routers.py        # Database routers для multi-DB
│   └── wsgi.py           # WSGI приложение
├── organizations/         # Приложение: организации ЦБ РФ
├── api/                   # Приложение: REST API
├── apps/                  # Папка для приложений
│   ├── accounts/         # Приложение: авторизация
│   ├── inventory/        # Приложение: склад
│   ├── builds/           # Приложение: сборки
│   └── dashboard/        # Приложение: дашборд
├── templates/             # HTML шаблоны
├── static/               # Статические файлы
├── gunicorn.conf.py     # Конфигурация Gunicorn
├── deploy.sh            # Скрипт деплоя (Linux)
├── requirements.txt     # Зависимости Python
├── ADD_NEW_APP.md      # Инструкция по добавлению приложений
└── README.md           # Этот файл
```

## Добавление новых приложений

Инструкция по добавлению новых приложений находится в `ADD_NEW_APP.md`.

Кратко:
1. Создать приложение: `python manage.py startapp myapp`
2. Добавить Router в `opencbbl/routers.py`
3. Добавить БД в `opencbbl/settings.py`
4. Добавить приложение в `INSTALLED_APPS`
5. Добавить URL префикс в `opencbbl/urls.py`
6. Применить миграции: `python manage.py migrate myapp --database=myapp_db`

## Деплой на production (без Docker)

### Автоматический деплой

```bash
chmod +x deploy.sh
./deploy.sh
```

Скрипт автоматически:
- Установит системные зависимости (Python, PostgreSQL, Nginx)
- Создаст виртуальное окружение
- Настроит PostgreSQL базы данных
- Применит миграции
- Соберет статические файлы
- Настроит systemd service
- Настроит Nginx

### Ручной деплой

1. **Установить зависимости**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx
```

2. **Настроить PostgreSQL**
```bash
sudo -u postgres psql -c "CREATE USER opencbbl WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "CREATE DATABASE opencbbl OWNER opencbbl;"
sudo -u postgres psql -c "CREATE DATABASE opencbbl_data OWNER opencbbl;"
sudo -u postgres psql -c "CREATE DATABASE pcmanager_data OWNER opencbbl;"
```

3. **Настроить проект**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Отредактируйте .env с вашими настройками
```

4. **Применить миграции**
```bash
python manage.py migrate --database=default
python manage.py migrate --database=opencbbl_db
python manage.py migrate --database=pcmanager_db
python manage.py collectstatic --noinput
```

5. **Настроить systemd service**
```bash
sudo cp gunicorn.conf.py /etc/gunicorn.d/opencbbl.py
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
```

6. **Настроить Nginx**
```bash
sudo cp /etc/nginx/sites-available/opencbbl
sudo ln -s /etc/nginx/sites-available/opencbbl /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

## Управление сервисом

```bash
# Проверить статус
sudo systemctl status opencbbl

# Перезапустить
sudo systemctl restart opencbbl

# Посмотреть логи
sudo journalctl -u opencbbl -f
```

## Безопасность в production

- Установите `DEBUG=False` в `.env`
- Используйте сильный `SECRET_KEY`
- Настройте SSL сертификат (Let's Encrypt)
- Используйте PostgreSQL вместо SQLite
- Ограничьте доступ к админке по IP

## Источники данных

- [ЦБ РФ Warning List API](https://cbr.ru/warninglistapi/swagger)
- [Список компаний с признаками нелегальной деятельности](https://cbr.ru/inside/warning-list/)

## Лицензия

MIT License

## Отказ от ответственности

Проект использует официальные открытые данные Центрального Банка РФ. Вся информация взята из публичного реестра и предоставляется "как есть" в информационных целях.
