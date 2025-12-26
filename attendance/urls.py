from django.urls import path, include
from attendance.views import AttendanceView
app_name = "attendance"

urlpatterns = [
    path('api/', include("attendance.api.urls")),
    path("attendance/", AttendanceView.as_view(), name="attendance"),

]