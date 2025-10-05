# emails/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from emails.api.views import EmailSenderViewSet

router = DefaultRouter()
router.register(r'email', EmailSenderViewSet, basename='email-sender')

urlpatterns = [
    path('', include(router.urls)),
]
