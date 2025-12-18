from django.urls import path, include
from .views import SchoolListView, SchoolProfileView, TestView

app_name="schools"

urlpatterns = [
    # 👇 API routes for schools
    path('api/', include('schools.api.urls')),
    path("schools/", SchoolListView.as_view(), name="list"),
    path("test/", TestView.as_view(), name="test"),
    path("schools/<slug:slug>/profile/", SchoolProfileView.as_view(), name="school-profile"),
    # path("schools/add/", SchoolOrgCreateView.as_view(), name="add")
]
