from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "layouts/base.html"

class AttendanceDashboardView(TemplateView):
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Example demo values (replace with actual DB queries later)
        total_strength = 100
        present = 78
        absent = total_strength - present

        context["total_strength"] = total_strength
        context["present"] = present
        context["absent"] = absent
        return context
