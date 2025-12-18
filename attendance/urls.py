from django.urls import path, include
app_name = "attendance"

urlpatterns = [
    path('api/', include("attendance.api.urls")),

]