from django.test import TestCase
# [urls.py]
from django.urls import path, include
from django.views.generic.base import RedirectView
from . import views



urlpatterns = [
# Create your tests here.
    path('users/', views.users_list, name='manage_users'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:user_id>/deactivate/', views.deactivate_user, name='deactivate_user'),
    path('users/<int:user_id>/unit/reset-password/', views.reset_unit_password, name='reset_unit_password'),
    path('users/<int:user_id>/assign-groups/', views.assign_groups_to_user, name='assign_groups'),
]