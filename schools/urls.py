from django.urls import path, include
from .views import SchoolListView #SchoolOrgCreateView

app_name="schools"

urlpatterns = [
    # 👇 API routes for schools
    path('api/', include('schools.api.urls')),
    path("schools/", SchoolListView.as_view(), name="list"),
    # path("schools/add/", SchoolOrgCreateView.as_view(), name="add")
]
