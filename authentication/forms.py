from django import forms
from .models import ApiKey


class ApiKeyForm(forms.ModelForm):
    class Meta:
        model = ApiKey
        fields = ["name", "is_active", "expires_at", "allowed_ip_address", "allowed_domain"]
        widgets = {
            "expires_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),  # HTML5 date-time picker
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set default initial values
        self.fields["is_active"].initial = True
        self.fields["expires_at"].initial = None
        self.fields["allowed_ip_address"].initial = ""
        self.fields["allowed_domain"].initial = ""

        # Add custom styles or attributes if needed
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})

        # Add is-invalid class if errors exist
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                field.widget.attrs.update({"class": "form-control is-invalid"})
