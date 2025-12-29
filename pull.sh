#!/bin/bash

git add .
git commit -m "Auto-commit before pulling latest changes"

# Pull latest changes from Git
echo "Pulling latest changes from Git..."
git pull  # Change 'main' to your branch if needed

# Run Django commands
echo "Collecting static files..."
python3 manage.py collectstatic --noinput

echo "Making migrations..."
python3 manage.py makemigrations

echo "Applying migrations..."
python3 manage.py migrate

# Change permissions
echo "Setting permissions for static files..."
chmod 755 static

# Restart services (requires sudo)
echo "Restarting Gunicorn, Daphne and Nginx (requires password)..."
sudo systemctl restart gunicorn && sudo systemctl restart nginx && sudo systemctl restart daphne

# Restart Celery and Celery Beat
echo "Restarting Celery worker..."
sudo systemctl restart celery

echo "Restarting Celery Beat..."
sudo systemctl restart celery-beat

echo "Deployment completed successfully! 🎉"
