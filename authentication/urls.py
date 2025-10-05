# [urls.py]
from django.urls import path, include
from . import views
app_name="authentication"

urlpatterns = [
    path('api/', include('authentication.api.urls')),
    # ACCOUNTS
    path('accounts/login/', views.login_view, name="login_view"),
    path('accounts/password-reset/request/', views.password_reset_request_view, name="password_reset_request_view"),
    path('accounts/reset-password/', views.reset_password, name="reset_password_view"),

    # UNAUTHORIZED
    path('unauthorized/token-expired/', views.token_expired, name="token_expired_view"),
    path('unauthorized/page/403/', views.page_403, name="page_403_view"),
    path('unauthorized/page/404/', views.page_404, name="page_404_view"),

    # API
    path('api/manage/list/', views.api_list, name='api_key_list'),
    path("api/manage/<int:pk>/update/", views.ApiKeyUpdateView.as_view(), name="api_key_update"),
]