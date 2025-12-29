from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User, Group
from users.models import UserProfile, Organization, Designation


# =====================================================
# ORGANIZATION FORM
# =====================================================

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = [
            'name', 'description', 'address',
            'contact_person', 'contact_number',
            'email', 'website'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', '')
            field.widget.attrs['class'] += ' form-control'
            field.widget.attrs.setdefault('placeholder', field.label)


# =====================================================
# USER PROFILE ADMIN FORM (SAFE)
# =====================================================

class UserProfileAdminForm(forms.ModelForm):
    position = forms.ChoiceField(
        choices=[('', '--- Select Position ---')],
        required=False,
        label="Position (from Group)"
    )

    class Meta:
        model = UserProfile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.fields['position'].choices += [
                (g.name, g.name) for g in Group.objects.all()
            ]
        except Exception:
            # DB not ready during migrate
            pass


# =====================================================
# USER GROUP VALIDATOR
# =====================================================

class UserGroupConfig:
    @staticmethod
    def validate_group_limit(value):
        if len(value) > 5:
            raise ValidationError('You can select at most 5 groups.')


# =====================================================
# ADD USER FORM (SAFE)
# =====================================================

class AddUserForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput)

    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Assign Groups"
    )

    organizations = forms.ModelMultipleChoiceField(
        queryset=Organization.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'}),
    )

    default_organization = forms.ModelChoiceField(
        queryset=Organization.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control select2'}),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            # self.fields['groups'].queryset = Group.objects.filter(
            #     name__in=['COOP Manager', 'COOP Supervisor']
            # )
            self.fields['organizations'].queryset = Organization.objects.all()
            self.fields['default_organization'].queryset = Organization.objects.all()
        except Exception:
            pass

        for field in self.fields.values():
            field.widget.attrs.setdefault('class', '')
            field.widget.attrs['class'] += ' form-control'


# =====================================================
# USER GROUP FORM (SAFE)
# =====================================================

class UserGroupForm(forms.Form):
    designations = forms.ModelMultipleChoiceField(
        queryset=Designation.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        validators=[UserGroupConfig.validate_group_limit],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.fields['designations'].queryset = Designation.objects.all()
        except Exception:
            pass


# =====================================================
# USER EDIT FORM
# =====================================================

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


# =====================================================
# USER PROFILE FORM (SAFE)
# =====================================================

class UserProfileForm(forms.ModelForm):
    gender = forms.ChoiceField(
        choices=[('', '--- Select Gender ---')] + list(
            UserProfile._meta.get_field('gender').choices
        ),
        required=False,
    )

    position = forms.ChoiceField(
        choices=[('', '--- Select Position ---')],
        required=False,
    )

    organizations = forms.ModelMultipleChoiceField(
        queryset=Organization.objects.none(),
        required=False,
    )

    default_organization = forms.ModelChoiceField(
        queryset=Organization.objects.none(),
        required=False,
    )

    class Meta:
        model = UserProfile
        fields = [
            'profile_picture', 'gender',
            'position', 'organizations',
            'default_organization'
        ]

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)

        try:
            self.fields['position'].choices += [
                (g.name, g.name)
                for g in Group.objects.exclude(
                    name__in=['Superusers', 'Admins']
                )
            ]
            self.fields['organizations'].queryset = Organization.objects.all()
            self.fields['default_organization'].queryset = Organization.objects.all()
        except Exception:
            pass

        if instance:
            self.fields['organizations'].initial = instance.organizations.all()
            self.fields['default_organization'].initial = instance.default_organization


# =====================================================
# RESET PASSWORD FORM
# =====================================================

class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        data = super().clean()
        if data.get('new_password') != data.get('confirm_password'):
            raise ValidationError("Passwords do not match.")
        return data
