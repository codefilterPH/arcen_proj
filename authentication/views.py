from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from authentication.utils.check_role import CheckUserPermission
from authentication.models import ApiKey
from authentication.forms import ApiKeyForm
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from authentication.utils.token_validation import TokenValidator

def login_view(request):
    return render(request, 'authentication/login.html')  # Ensure the template is in 'templates/coop_hub'

def password_reset_request_view(request):
    return render(request, 'authentication/password/password_reset_request.html')

def reset_password(request):
    uid = request.GET.get('uid')
    token = request.GET.get('token')

    if not uid or not token:
        return redirect(reverse('authentication:page_403_view'))

    validator = TokenValidator(token, uid, debug=True)
    redirect_response = validator.validate_or_redirect()
    if redirect_response:
        return redirect_response

    try:
        user = User.objects.get(pk=uid)
    except User.DoesNotExist:
        return redirect(reverse('authentication:page_403_view'))


    return render(request, 'authentication/password/reset_password.html', {
        'uid': uid,
        'token': token,
        'user': user.userprofile
    })

def token_expired(request):
    return render(request, 'authentication/errors/token_expired.html')

def page_403(request):
    return render(request, 'authentication/errors/page_403.html')

def page_404(request):
    return render(request, 'authentication/errors/page_404.html')


# API KEY MANAGE BEGIN
@login_required
@CheckUserPermission.role_required(group_names='Developer')
def api_list(request):
    context = {}
    return render(request, 'authentication/api/list.html', context)

@method_decorator(login_required, name='dispatch')
@method_decorator(CheckUserPermission.role_required(group_names=['Developer']), name='dispatch')
class ApiKeyUpdateView(UpdateView):
    model = ApiKey
    form_class = ApiKeyForm
    template_name = "authentication/api/forms.html"
    success_url = reverse_lazy("api_key_list")  # Redirect to the list view after updating

    def get_initial(self):
        """
        Set initial values for the form fields.
        """
        initial = super().get_initial()
        api_key = self.get_object()
        initial.update({
            "is_active": api_key.is_active,
            "expires_at": api_key.expires_at,
            "allowed_ip_address": api_key.allowed_ip_address,
            "allowed_domain": api_key.allowed_domain,
        })
        return initial
