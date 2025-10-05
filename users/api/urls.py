from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.api import views

# Initialize the router
router = DefaultRouter()

# Register the UserProfileViewSet with the router
router.register(r'user-profile', views.UserProfileViewSet, basename='user-profile')
router.register(r'users', views.ManageUsers, basename='get-users')
router.register(r'organizations', views.OrganizationViewSet, basename='organization')
router.register(r'designations', views.DesignationViewSet, basename='designation')
router.register(r'classifications', views.ClassificationViewSet, basename='classification')
router.register(r'users-list', views.UserListViewSet, basename='search-users')

urlpatterns = [
    path('', include(router.urls)),  # Include the router's generated URLs
]
