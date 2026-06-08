# Пошаговая инструкция деплоя на VPS

## Информация о сервере
- **IP**: 170.168.1.221
- **Домен**: mikesdemos.ru
- **Поддомен для проекта**: pcmanager.mikesdemos.ru
- **Порт Gunicorn**: 8001

## Шаг 1: Подключение к VPS

```bash
ssh user@170.168.1.221
```

## Шаг 2: Создание базы данных PostgreSQL

```bash
sudo -u postgres psql
```

Внутри psql выполните:

```sql
CREATE DATABASE pcmanager_db;
CREATE USER pcmanager_user WITH PASSWORD 'ВАШ_ПАРОЛЬ';
GRANT ALL PRIVILEGES ON DATABASE pcmanager_db TO pcmanager_user;
ALTER USER pcmanager_user CREATEDB;
\q
```

**Важно**: Запомните пароль, он понадобится в шаге 5.

## Шаг 3: Клонирование репозитория

```bash
cd /tmp
git clone https://github.com/MichaelUniHorus/pcmanager.git
cd pcmanager
```

## Шаг 4: Запуск скрипта деплоя

```bash
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

Скрипт автоматически:
- Создаст директорию `/var/www/pcmanager`
- Клонирует репозиторий
- Создаст виртуальное окружение
- Установит зависимости
- Создаст `.env` файл
- Применит миграции
- Соберёт статику
- Настроит systemd
- Настроит nginx

## Шаг 5: Настройка .env файла

Отредактируйте `/var/www/pcmanager/.env`:

```bash
sudo nano /var/www/pcmanager/.env
```

Замените `CHANGE_ME_PASSWORD` на пароль из шага 2:

```env
DEBUG=False
SECRET_KEY=сгенерированный_ключ
ALLOWED_HOSTS=pcmanager.mikesdemos.ru,localhost,127.0.0.1
DATABASE_URL=postgresql://pcmanager_user:ВАШ_ПАРОЛЬ@localhost/pcmanager_db
```

Сохраните (Ctrl+O, Enter) и выйдите (Ctrl+X).

## Шаг 6: Повторное применение миграций

```bash
cd /var/www/pcmanager
source venv/bin/activate
python manage.py migrate --settings=config.settings.prod
```

## Шаг 7: Перезапуск сервисов

```bash
sudo systemctl restart pcmanager
sudo systemctl reload nginx
```

## Шаг 8: Настройка DNS

Добавьте DNS запись на вашем регистраторе домена:

| Тип | Имя | Значение |
|-----|-----|---------|
| A   | pcmanager | 170.168.1.221 |

Это создаст поддомен `pcmanager.mikesdemos.ru`

## Шаг 9: Настройка SSL (Let's Encrypt)

```bash
sudo certbot --nginx -d pcmanager.mikesdemos.ru
```

Следуйте инструкциям certbot (введите email, согласитесь с условиями).

## Шаг 10: Проверка работы

```bash
# Проверка статуса gunicorn
sudo systemctl status pcmanager

# Проверка логов
sudo journalctl -u pcmanager -f

# Проверка nginx
sudo nginx -t
```

Откройте в браузере: https://pcmanager.mikesdemos.ru

## Загрузка тестовых данных (опционально)

```bash
cd /var/www/pcmanager
source venv/bin/activate
python manage.py seed --settings=config.settings.prod
```

Создаст:
- 8 категорий компонентов
- 16 компонентов с ценами
- Admin user: `admin` / `admin123`

## Управление проектом

### Перезапуск gunicorn
```bash
sudo systemctl restart pcmanager
```

### Просмотр логов
```bash
sudo journalctl -u pcmanager -f
```

### Обновление проекта
```bash
cd /var/www/pcmanager
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --settings=config.settings.prod
python manage.py collectstatic --noinput --settings=config.settings.prod
sudo systemctl restart pcmanager
```

## Структура проекта на VPS

```
/var/www/pcmanager/
├── apps/                    # Django приложения
├── config/                  # Настройки Django
├── deploy/                  # Конфиги деплоя
├── manage.py                # Django manage
├── requirements.txt         # Зависимости
├── static/                  # Статические файлы
├── templates/               # Шаблоны
├── venv/                    # Виртуальное окружение
└── .env                     # Переменные окружения
```

## Решение проблем

### Ошибка подключения к БД
Проверьте пароль в `.env` и права пользователя в PostgreSQL:
```bash
sudo -u postgres psql
\l                    # список баз
\du                   # список пользователей
```

### Ошибка 502 Bad Gateway
Проверьте статус gunicorn:
```bash
sudo systemctl status pcmanager
sudo journalctl -u pcmanager -n 50
```

### Статические файлы не загружаются
Проверьте права:
```bash
sudo chown -R www-data:www-data /var/www/pcmanager/static
```

### Ошибка миграций
Удалите миграции и примените заново:
```bash
cd /var/www/pcmanager
find apps -name "*.pyc" -delete
find apps -name "__pycache__" -type d -delete
source venv/bin/activate
python manage.py migrate --settings=config.settings.prod
```
