#!/bin/bash

echo "Freezing dependencies to requirements.txt..."
pip freeze > requirements.txt

echo "Collecting static files..."
python3 manage.py collectstatic --noinput

echo "Making migrations..."
python3 manage.py makemigrations

echo "Applying migrations..."
python3 manage.py migrate

echo "Staging all changes..."
git add .

# Prompt for commit message
read -p "Enter commit message: " commit_message

echo "Committing changes..."
git commit -m "$commit_message"

echo "Pushing to remote repository..."
git push

echo "🚀 Deployment completed successfully!"
