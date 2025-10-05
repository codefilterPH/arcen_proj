from django.urls import path, include
from users.views import *
app_name = "users"

urlpatterns = [
    path('api/', include("users.api.urls")),
    # PROFILE
    path('profile/', profile_view, name='profile_view'),
    path('password/change/', password_change_view, name='password_change_view'),
    path('user/sign/', esign_view, name='esign_view'),
    path('user/update-profile/', update_profile_view, name='update_profile_view'),

    # USERS MANAGEMENT
    path('users/', users_list, name='manage_users'),
    path('users/new/', add_user_view, name='add_user_view'),
    path('users/<int:user_id>/edit/', edit_user, name='edit_user'),
    path('manage-users/<int:user_id>/activate/', activate_user, name='activate_user'),
    path('users/<int:user_id>/deactivate/', deactivate_user, name='deactivate_user'),
    path('users/<int:user_id>/unit/reset-password/', reset_unit_password, name='reset_unit_password'),
    path('users/<int:user_id>/assign-groups/', assign_designations_to_user, name='assign_groups'),

    # ORGANIZATION
    path('organization/add/', OrganizationCreateView.as_view(), name='org_add'),
    path('organization/<int:pk>/edit/', OrganizationUpdateView.as_view(), name='org_edit'),
]