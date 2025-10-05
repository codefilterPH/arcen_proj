# schools/forms.py
from django import forms
from .models import SchoolOrg

class SchoolOrgForm(forms.ModelForm):
    class Meta:
        model = SchoolOrg
        fields = ["logo", "name", "address"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter school name"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Enter address"}),
            "logo": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
