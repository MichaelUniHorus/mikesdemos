#!/bin/bash
# Deployment script for opencbbl (without Docker)

set -e

echo "=== Deploying opencbbl to production (without Docker) ==="

# 1. Install system dependencies
echo "1. Installing system dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx

# 2. Setup PostgreSQL
echo "2. Setting up PostgreSQL..."
sudo -u postgres psql -c "CREATE USER opencbbl WITH PASSWORD 'YOUR_STRONG_PASSWORD';" || true
sudo -u postgres psql -c "CREATE DATABASE opencbbl OWNER opencbbl;" || true
sudo -u postgres psql -c "CREATE DATABASE opencbbl_data OWNER opencbbl;" || true
sudo -u postgres psql -c "CREATE DATABASE pcmanager_data OWNER opencbbl;" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE opencbbl TO opencbbl;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE opencbbl_data TO opencbbl;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE pcmanager_data TO opencbbl;"

# 3. Create virtual environment
echo "3. Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 4. Install Python dependencies
echo "4. Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 5. Create .env file if not exists
echo "5. Setting up .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Please edit .env file with your actual settings"
fi

# 6. Run migrations for all databases
echo "6. Running migrations..."
python manage.py migrate --database=default
python manage.py migrate --database=opencbbl_db
python manage.py migrate --database=pcmanager_db

# 7. Collect static files
echo "7. Collecting static files..."
python manage.py collectstatic --noinput

# 8. Create superuser (optional)
echo "8. Creating superuser (optional)..."
python manage.py createsuperuser --noinput || echo "Superuser already exists or creation skipped"

# 9. Setup systemd service
echo "9. Setting up systemd service..."
sudo tee /etc/systemd/system/opencbbl.service > /dev/null << EOF
[Unit]
Description=opencbbl Django application
After=network.target postgresql.service

[Service]
User=$USER
Group=www-data
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
ExecStart=$(pwd)/venv/bin/gunicorn --config gunicorn.conf.py opencbbl.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 10. Setup Nginx
echo "10. Setting up Nginx..."
sudo tee /etc/nginx/sites-available/opencbbl > /dev/null << EOF
server {
    listen 80;
    server_name mikesdemos.ru www.mikesdemos.ru;

    location /static/ {
        alias $(pwd)/staticfiles/;
    }

    location /media/ {
        alias $(pwd)/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/opencbbl /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 11. Enable and start service
echo "11. Starting systemd service..."
sudo systemctl daemon-reload
sudo systemctl enable opencbbl
sudo systemctl restart opencbbl

echo "=== Deployment complete ==="
echo "Application should be available at http://mikesdemos.ru"
echo "Check service status: sudo systemctl status opencbbl"
echo "View logs: sudo journalctl -u opencbbl -f"
