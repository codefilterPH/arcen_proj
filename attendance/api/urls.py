from rest_framework.routers import DefaultRouter
from attendance.api.views import AttendanceViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'attendance', AttendanceViewSet, basename='attendance')

urlpatterns = [
    path("", include(router.urls)),
]
