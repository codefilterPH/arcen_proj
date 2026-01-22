from .settings import *
import os


# For serving static files in development
# For serving static files in development
STATICFILES_DIRS = [
    BASE_DIR / "authentication" / "static",
    BASE_DIR / "qrscanner" / "static",
    BASE_DIR / "dashboard" / "static",
    BASE_DIR / "users" / "static",
    # BASE_DIR / "attendance" / "static",
    BASE_DIR / "schools" / "static",
    BASE_DIR / "school" / "static",
    BASE_DIR / "student" / "static",
]


# STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_ROOT = BASE_DIR / "static"

STATIC_URL = "/static/"
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# if DEBUG:
#     STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
# else:
#     STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]


ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.1.49',
            '10.169.97.31',
         ]
# SECURITY WARNING: keep the secret key used in production secret
SECRET_KEY = os.getenv("SECRET_KEY")
# SECURITY WARNING: define the correct hosts in production!
# ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", default="*").split(',')

CSRF_TRUSTED_ORIGINS = [
    "https://192.168.1.49:8888",
]
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

