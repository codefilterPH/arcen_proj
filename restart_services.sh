#!/bin/bash
# Restart Django-related services (Daphne, Celery, Gunicorn) + Nginx

echo "🚀 Restarting Daphne..."
sudo systemctl restart daphne.service

echo "🚀 Restarting Celery (worker)..."
sudo systemctl restart celery.service

# If you run a beat scheduler, include this too
echo "🚀 Restarting Celery Beat..."
sudo systemctl restart celery-beat.service

echo "🚀 Restarting Celery Messages..."
sudo systemctl restart celery_message.service

echo "🚀 Restarting Celery Default..."
sudo systemctl restart celery_default.service

echo "🚀 Restarting Celery Beat..."
sudo systemctl restart celery-beat.service

echo "🚀 Restarting Gunicorn..."
sudo systemctl restart gunicorn.service

echo "🚀 Restarting Nginx..."
sudo systemctl restart nginx.service

echo "✅ All services restarted successfully."
