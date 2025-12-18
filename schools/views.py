from django.views.generic import ListView
from .models import SchoolOrg
from django.views.generic import CreateView, DetailView
from django.urls import reverse_lazy
from schools.forms import SchoolOrgForm
from django.contrib import messages

class SchoolListView(ListView):
    model = SchoolOrg
    template_name = "schools/schools.html"
    context_object_name = "schools"
    ordering = ["name"]  # optional: sort alphabetically

class SchoolProfileView(DetailView):
    model = SchoolOrg
    template_name = "schools/school_profile.html"
    context_object_name = "school"
    slug_field = "slug"           # model field to match
    slug_url_kwarg = "slug"       # URL param name

# class SchoolOrgCreateView(CreateView):
#     model = SchoolOrg
#     form_class = SchoolOrgForm
#     template_name = "schools/add_school.html"  # not needed if using modal only
#     success_url = reverse_lazy("schools:list")  # adjust to your list view name
#
#     def form_valid(self, form):
#         messages.success(self.request, "✅ School added successfully.")
#         return super().form_valid(form)
#
#     def form_invalid(self, form):
#         messages.error(self.request, "❌ Please correct the errors below.")
#         return super().form_invalid(form)