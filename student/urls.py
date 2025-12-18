from django.urls import path, include
from student.views import *
app_name = "student"

urlpatterns = [
    path('api/', include("student.api.urls")),
]