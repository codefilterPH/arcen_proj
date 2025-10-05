from rest_framework.routers import DefaultRouter
from .views import SchoolOrgViewSet

router = DefaultRouter()
router.register(r'schools', SchoolOrgViewSet, basename='schoolorg')

urlpatterns = router.urls
