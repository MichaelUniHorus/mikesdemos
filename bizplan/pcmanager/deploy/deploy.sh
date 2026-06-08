#!/bin/bash

# Деплой pcmanager на VPS: 170.168.1.221, mikesdemos.ru

set -e

# Конфигурация
PROJECT_NAME="pcmanager"
PROJECT_DIR="/var/www/$PROJECT_NAME"
DOMAIN="pcmanager.mikesdemos.ru"
VENV_DIR="$PROJECT_DIR/venv"
GIT_REPO="https://github.com/MichaelUniHorus/pcmanager.git"
BRANCH="main"

echo "=== Деплой $PROJECT_NAME на 170.168.1.221 ==="

# 1. Создание директории проекта
echo "Создание директории проекта..."
sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR

# 2. Клонирование репозитория
if [ -d "$PROJECT_DIR/.git" ]; then
    echo "Обновление репозитория..."
    cd $PROJECT_DIR
    git pull origin $BRANCH
else
    echo "Клонирование репозитория..."
    git clone $GIT_REPO $PROJECT_DIR
    cd $PROJECT_DIR
    git checkout $BRANCH
fi

# 3. Создание виртуального окружения
if [ ! -d "$VENV_DIR" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv $VENV_DIR
fi

# 4. Активация и установка зависимостей
echo "Установка зависимостей..."
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. Создание .env файла
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "Создание .env файла..."
    cat > $PROJECT_DIR/.env << EOF
DEBUG=False
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
ALLOWED_HOSTS=$DOMAIN,localhost,127.0.0.1
DATABASE_URL=postgresql://pcmanager_user:CHANGE_ME_PASSWORD@localhost/pcmanager_db
EOF
    echo "ВНИМАНИЕ: Отредактируйте $PROJECT_DIR/.env и замените CHANGE_ME_PASSWORD на реальный пароль"
fi

# 6. Миграции
echo "Применение миграций..."
source $VENV_DIR/bin/activate
cd $PROJECT_DIR
python manage.py migrate --settings=config.settings.prod

# 7. Сборка статических файлов
echo "Сборка статических файлов..."
python manage.py collectstatic --noinput --settings=config.settings.prod

# 8. Создание директории для сокета
sudo mkdir -p /var/www/$PROJECT_NAME
sudo chown www-data:www-data /var/www/$PROJECT_NAME

# 9. Настройка systemd
echo "Настройка systemd..."
sudo cp $PROJECT_DIR/deploy/gunicorn.service /etc/systemd/system/$PROJECT_NAME.service
sudo systemctl daemon-reload
sudo systemctl enable $PROJECT_NAME
sudo systemctl restart $PROJECT_NAME

# 10. Настройка nginx
echo "Настройка nginx..."
sudo cp $PROJECT_DIR/deploy/nginx.conf /etc/nginx/sites-available/$PROJECT_NAME
sudo ln -sf /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled/$PROJECT_NAME
sudo nginx -t && sudo systemctl reload nginx

echo "=== Деплой завершен ==="
echo "Следующие шаги:"
echo "1. Создать БД PostgreSQL (см. инструкцию ниже)"
echo "2. Отредактировать $PROJECT_DIR/.env (заменить пароль)"
echo "3. Добавить DNS запись: pcmanager.mikesdemos.ru → 170.168.1.221"
echo "4. Настроить SSL: sudo certbot --nginx -d $DOMAIN"
