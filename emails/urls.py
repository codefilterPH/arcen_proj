from django.urls import path, include
from users.views import *
app_name = "emails"

urlpatterns = [
    path('api/', include("emails.api.urls")),
]