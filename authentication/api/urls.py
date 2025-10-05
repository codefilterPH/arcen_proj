
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
from authentication.api import views
app_name = 'authentication'

router.register(r'auth', views.UserLoginViewSet, basename='user-login')
router.register(r'api-manage', views.ApiKeyViewSet, basename='api_key_viewset')
router.register(r'password-reset', views.PasswordResetViewSet, basename='password-reset')
urlpatterns = [
    # RESTFUL
    path('', include((router.urls, 'api'), namespace='api')),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]