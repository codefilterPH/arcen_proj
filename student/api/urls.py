# urls.py
from rest_framework.routers import DefaultRouter
from student.api.views import StudentViewSet

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='students')

urlpatterns = router.urls
