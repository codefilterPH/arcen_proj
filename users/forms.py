from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User, Group
from users.models import UserProfile, Organization, Designation

class OrganizationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            # Add Bootstrap class to all form fields
            existing_class = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{existing_class} form-control".strip()

            # Optionally set placeholders or default values (for UI help)
            if not field.widget.attrs.get('placeholder'):
                field.widget.attrs['placeholder'] = field.label

            # You can also add default values like this, if needed:
            # if self.instance and getattr(self.instance, field_name, None):
            #     field.initial = getattr(self.instance, field_name)

    class Meta:
        model = Organization
        fields = [
            'name', 'description', 'address', 'contact_person',
            'contact_number', 'email', 'website'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }
        help_texts = {
            'name': 'The official name of the cooperative.',
            'email': 'Enter a valid email address.',
            'website': 'Optional website URL.',
        }

class UserProfileAdminForm(forms.ModelForm):
    position = forms.ChoiceField(
        choices=[('', '--- Select Position ---')] + [(g.name, g.name) for g in Group.objects.all()],
        required=False,
        label="Position (from Group)"
    )

    class Meta:
        model = UserProfile
        fields = '__all__'

class UserGroupConfig:
    @staticmethod
    def validate_group_limit(value):
        if len(value) > 5:
            raise ValidationError('You can select at most 5 groups.')

config = UserGroupConfig()


class AddUserForm(forms.ModelForm):
    """Form for adding a new User and UserProfile with coopp6yerative assignment."""

    # User model fields
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True)

    # Group selection
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.filter(name__in=['COOP Manager', 'COOP Supervisor']),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Assign Groups"
    )

    # Profile fields
    gender = forms.ChoiceField(
        choices=UserProfile.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    profile_picture = forms.ImageField(required=False)

    # Cooperative assignments
    organizations = forms.ModelMultipleChoiceField(
        queryset=Organization.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        required=False,  # Now always optional in form-level
        label="Assign Organizations"
    )

    default_organization = forms.ModelChoiceField(
        queryset=Organization.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2'}),
        required=False,  # Now always optional in form-level
        label="Default Organization"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']



class UserGroupForm(forms.Form):
    """Form for assigning designations to a user."""

    designations = forms.ModelMultipleChoiceField(
        queryset=Designation.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Select Designation (Select 1 to 5 designations)",
        required=False,
        validators=[UserGroupConfig.validate_group_limit]
    )

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply bootstrap classes to each form field
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class UserProfileForm(forms.ModelForm):
    gender = forms.ChoiceField(
        choices=[('', '--- Select Gender ---')] + list(UserProfile._meta.get_field('gender').choices),
        required=False,
        label='Gender'
    )

    position = forms.ChoiceField(
        choices=[('', '--- Select Position ---')] + [
            (g.name, g.name) for g in Group.objects.exclude(name__in=['Superusers', 'Admins'])
        ],
        required=False,
        label="Position (from Group)"
    )

    # Add organizations: multi-select field for ManyToMany
    organizations = forms.ModelMultipleChoiceField(
        queryset=Organization.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label="Organizations"
    )

    # Add default_organization: single select field for ForeignKey
    default_organization = forms.ModelChoiceField(
        queryset=Organization.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Default Organization"
    )

    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'gender', 'position', 'organizations', 'default_organization']

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

        if instance and instance.position:
            self.fields['position'].initial = instance.position

        if instance and instance.gender:
            self.fields['gender'].initial = instance.gender

        if instance:
            self.fields['organizations'].initial = instance.organizations.all()
            self.fields['default_organization'].initial = instance.default_organization

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'
        }),
        required=True,
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        }),
        required=True,
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data