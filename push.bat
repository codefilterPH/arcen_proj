@echo off
echo Freezing dependencies to requirements.txt...
pip freeze > requirements.txt

echo Collecting static files...
py manage.py collectstatic --noinput

echo Making migrations...
py manage.py makemigrations

echo Applying migrations...
py manage.py migrate

echo Staging all changes...
git add .

:: Prompt for commit message
set /p commit_message="Enter commit message: "

echo Committing changes...
git commit -m "%commit_message%"

echo Pushing to remote repository...
git push

echo 🚀 Deployment completed successfully!
exit
