from rest_framework.routers import DefaultRouter
from .views import SchoolOrgViewSet, SchoolYearViewSet

router = DefaultRouter()
router.register(r'schools', SchoolOrgViewSet, basename='schoolorg')
router.register(r'academic-years', SchoolYearViewSet, basename='academic-years')

urlpatterns = router.urls
