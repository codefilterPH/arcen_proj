from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from authentication.utils.check_role import CheckUserPermission

class RoleRequiredMixin:
    """
    Mixin to ensure that a user belongs to one of the specified groups.
    Can be used in class-based views (CBVs).

    SAMPLE:
    class LendingGroupView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
        template_name = 'lending/group/load-groups.html'
        allowed_roles = ['Developer', 'COOP Manager', 'COOP Supervisor']
    """
    allowed_roles = ['Developer', 'COOP Manager', 'COOP Supervisor']

    def dispatch(self, request, *args, **kwargs):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return redirect('authentication:login_view')  # Redirect to login page if not authenticated

        # Ensure user is in the correct group(s)
        if not CheckUserPermission.check_role(request.user, self.allowed_roles):
            return redirect('authentication:page_403_view')

        return super().dispatch(request, *args, **kwargs)
