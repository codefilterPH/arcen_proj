from authentication.utils.check_role import CheckUserPermission
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from users.models import UserProfile, Organization
from users.forms import (
    UserEditForm, UserProfileForm, ResetPasswordForm, UserGroupForm,
    AddUserForm, OrganizationForm
)
from django.contrib.auth.models import Group
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.conf import settings


class OrganizationCreateView(LoginRequiredMixin, CreateView):
    model = Organization
    form_class = OrganizationForm
    template_name = 'users/organization/form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Organization created successfully.")
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        return redirect('users:manage_users')

class OrganizationUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Organization
    form_class = OrganizationForm
    template_name = 'users/organization/form.html'

    def form_valid(self, form):
        messages.success(self.request, "Organization updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('organization:coop_edit', kwargs={'pk': self.object.pk})

    def test_func(self):
        organization = self.get_object()
        return self.request.user == organization.owner or self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to edit this organization.")
        return redirect('users:manage_users')

@login_required
def update_profile_view(request):
    """Not necessary template was used as included"""
    return render(request, 'users/profile/update-profile.html', {})

@login_required
def esign_view(request):
    context = {}
    return render(request, 'users/profile/esign.html', context)

@login_required
def password_change_view(request):
    return render(request, 'users/profile/password-change.html')

@login_required
def profile_view(request):
    context = {}
    return render(request, 'users/profile/profile.html', context)


@login_required
@CheckUserPermission.role_required(group_names=settings.ALLOWED_ROLE_USERS_MANAGEMENT)
def users_list(request):
    """Not necessary template was used as included"""
    return render(request, 'users/list-users.html', {})


@login_required
@CheckUserPermission.role_required(group_names=settings.ALLOWED_ROLE_USERS_MANAGEMENT)
def add_user_view(request):
    if request.method == 'POST':
        print("🟡 Received POST request to create user.")
        form = AddUserForm(request.POST, request.FILES)

        if form.is_valid():
            print("✅ Form is valid. Creating user...")
            print("📦 Cleaned data:", form.cleaned_data)

            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                password=form.cleaned_data['password'],
            )

            # Assign groups
            user.groups.set(form.cleaned_data['groups'])
            print("🔐 Groups assigned:", [g.name for g in form.cleaned_data['groups']])

            profile, created = UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    'gender': form.cleaned_data['gender'],
                    'profile_picture': form.cleaned_data.get('profile_picture'),
                    'default_organization': form.cleaned_data['default_organization'],
                }
            )

            # Assign orgs
            profile.organizations.set(form.cleaned_data['organizations'])

            # 🔑 Auto-generate QR code (base64)
            print("📲 Generating QR code for new user...")
            profile.generate_qr_code(force=True)
            profile.save(update_fields=["qr_code"])
            print("✅ QR code generated (base64 length:", len(profile.qr_code), ")")

            print("👤 UserProfile created for user:", user.username)
            return redirect('users:manage_users')

        else:
            print("❌ Form is invalid.")
            print("🛑 Errors:")
            for field, errors in form.errors.items():
                for error in errors:
                    print(f" - {field}: {error}")
    else:
        print("🟢 GET request received. Displaying empty form.")
        form = AddUserForm()

    return render(request, 'users/add_user.html', {'form': form})


@login_required
@CheckUserPermission.role_required(group_names=settings.ALLOWED_ROLE_USERS_MANAGEMENT)
def edit_user(request, user_id):
    print(f"🔍 edit_user view called with user_id={user_id}")  # debug

    user = get_object_or_404(User, id=user_id)
    user_profile = get_object_or_404(UserProfile, user=user)
    print(f"➡️ Editing User: {user.username} (ID={user.id})")
    print(f"➡️ UserProfile ID={user_profile.id}")

    if request.method == 'POST':
        print("📥 Received POST request for editing user")
        print(f"POST data: {request.POST}")
        print(f"FILES data: {request.FILES}")

        user_edit_form = UserEditForm(request.POST, instance=user)
        user_profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)

        if user_edit_form.is_valid() and user_profile_form.is_valid():
            print("✅ Both forms are valid, saving changes...")
            user_edit_form.save()
            user_profile_form.save()

            # 🔑 Always ensure QR exists or refresh it
            if not user_profile.qr_code:
                print("📲 No QR found. Generating new QR code...")
            else:
                print("♻️ Updating QR code (regenerating base64)...")

            user_profile.generate_qr_code(force=True)
            user_profile.save(update_fields=["qr_code"])
            print("✅ QR code updated (base64 length:", len(user_profile.qr_code), ")")

            messages.success(request, "User details updated successfully.")
            return redirect('users:manage_users')
        else:
            print("❌ Form validation failed")
            print("UserEditForm errors:", user_edit_form.errors)
            print("UserProfileForm errors:", user_profile_form.errors)
            messages.error(request, "There were errors in the form.")
    else:
        print("➡️ GET request – loading forms with current user data")
        user_edit_form = UserEditForm(instance=user)
        user_profile_form = UserProfileForm(instance=user_profile)

    print("📤 Rendering edit-user.html template")
    return render(request, 'users/edit-user.html', {
        'user': user,
        'user_profile': user_profile,
        'user_edit_form': user_edit_form,
        'user_profile_form': user_profile_form,
    })


@login_required
@CheckUserPermission.role_required(group_names=settings.ALLOWED_ROLE_USERS_MANAGEMENT)
def deactivate_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        try:
            user.is_active = False
            user.save()
            messages.success(request, "User has been deactivated successfully.")
            return redirect('users:manage_users')  # Redirect to the user management page
        except Exception as e:
            messages.error(request, f"Error deactivating user: {str(e)}")
            return redirect('users:manage_users')

    return render(request, 'users/deactivate-user.html', {'user': user})



@permission_classes([IsAuthenticated])
@CheckUserPermission.role_required(group_names=settings.ALLOWED_ROLE_USERS_MANAGEMENT)
def activate_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        try:
            user.is_active = True
            user.save()
            messages.success(request, "User has been activated successfully.")
            return redirect('users:manage_users')  # Redirect to the user management page
        except Exception as e:
            messages.error(request, f"Error activating user: {str(e)}")
            return redirect('users:manage_users')

    return render(request, 'users/activate-user.html', {'user': user})

@login_required
@CheckUserPermission.role_required(group_names=settings.ALLOWED_ROLE_USERS_MANAGEMENT)
def reset_unit_password(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        reset_password_form = ResetPasswordForm(request.POST)

        if reset_password_form.is_valid():
            new_password = reset_password_form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # Keep the user logged in after password change
            messages.success(request, "Password has been reset successfully.")
            return redirect('users:manage_users')  # Redirect to the user management page
        else:
            messages.error(request, "There was an error with the password reset form.")
    else:
        reset_password_form = ResetPasswordForm()

    return render(request, 'users/unit-reset-password.html', {
        'user': user,
        'reset_password_form': reset_password_form,
    })


# views.py
@login_required
@CheckUserPermission.role_required(group_names=settings.ALLOWED_ROLE_USERS_MANAGEMENT)
def assign_designations_to_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user_profile = user.userprofile  # assumes OneToOne is created

    if request.method == 'POST':
        form = UserGroupForm(request.POST)

        if form.is_valid():
            selected_designations = form.cleaned_data['designations']
            user_profile.designations.set(selected_designations)  # ✅ save assignment
            user_profile.save()

            messages.success(request, f"Designations successfully updated for {user.username}.")
            return redirect(reverse('users:manage_users'))
        else:
            messages.error(request, "Please select at least 1 and at most 5 designations.")
    else:
        form = UserGroupForm(initial={'designations': user_profile.designations.all()})

    return render(request, 'users/assign-role.html', {
        'user': user,
        'form': form,
    })
