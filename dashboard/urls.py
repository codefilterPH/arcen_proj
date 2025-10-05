# app/urls.py
from django.urls import path
from dashboard.views import AttendanceDashboardView, IndexView

urlpatterns = [
    path("", IndexView.as_view(), name="index_view"),
    path("dashboard/", AttendanceDashboardView.as_view(), name="attendance_dashboard"),
]
