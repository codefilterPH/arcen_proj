# Pull latest changes from Git
Write-Host "Pulling latest changes from Git..."
git pull  # Change 'main' to your branch if needed

# Run Django commands
Write-Host "Collecting static files..."
python manage.py collectstatic --noinput

Write-Host "Making migrations..."
python manage.py makemigrations

Write-Host "Applying migrations..."
python manage.py migrate