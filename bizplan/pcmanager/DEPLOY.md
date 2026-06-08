# Деплой на VPS с существующим Django проектом

## Предварительные требования

На VPS уже должны быть установлены:
- Python 3.10+
- PostgreSQL
- Nginx
- Git

## Шаги деплоя

### 1. Подключение к VPS

```bash
ssh user@your-vps-ip
```

### 2. Создание базы данных PostgreSQL

```bash
sudo -u postgres psql
CREATE DATABASE pcmanager_db;
CREATE USER pcmanager_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE pcmanager_db TO pcmanager_user;
\q
```

### 3. Клонирование и запуск скрипта деплоя

```bash
cd /tmp
git clone https://github.com/MichaelUniHorus/pcmanager.git
cd pcmanager
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

### 4. Настройка .env файла

Отредактируйте `/var/www/pcmanager/.env`:

```env
DEBUG=False
SECRET_KEY=ваш_секретный_ключ
ALLOWED_HOSTS=pcmanager.yourdomain.com,localhost,127.0.0.1
DATABASE_URL=postgresql://pcmanager_user:your_password@localhost/pcmanager_db
```

### 5. Настройка домена

Добавьте A запись в DNS:
- `pcmanager.yourdomain.com` → IP вашего VPS

### 6. Настройка SSL (Let's Encrypt)

```bash
sudo certbot --nginx -d pcmanager.yourdomain.com
```

### 7. Загрузка тестовых данных (опционально)

```bash
cd /var/www/pcmanager
source venv/bin/activate
python manage.py seed --settings=config.settings.prod
```

## Структура деплоя

- **Путь проекта**: `/var/www/pcmanager`
- **Виртуальное окружение**: `/var/www/pcmanager/venv`
- **Gunicorn socket**: `/var/www/pcmanager/pcmanager.sock`
- **Systemd service**: `pcmanager.service`
- **Nginx config**: `/etc/nginx/sites-available/pcmanager`

## Управление сервисом

```bash
# Перезапуск gunicorn
sudo systemctl restart pcmanager

# Проверка статуса
sudo systemctl status pcmanager

# Просмотр логов
sudo journalctl -u pcmanager -f

# Перезагрузка nginx
sudo systemctl reload nginx
```

## Обновление проекта

```bash
cd /var/www/pcmanager
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --settings=config.settings.prod
python manage.py collectstatic --noinput --settings=config.settings.prod
sudo systemctl restart pcmanager
```

## Различия от существующего проекта

- **Порт Gunicorn**: 8001 (чтобы не конфликтовать с существующим проектом на 8000)
- **Домен**: pcmanager.yourdomain.com (поддомен основного домена)
- **База данных**: отдельная база pcmanager_db
- **Systemd service**: pcmanager.service (отдельный сервис)
