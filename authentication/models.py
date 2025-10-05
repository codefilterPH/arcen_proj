from django.db import models

# Create your models here.
from datetime import timezone
from django.db import models
from django.contrib.auth.models import User
from authentication.utils.thread_locals import get_current_user
import secrets

class TrackingModel(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_%(class)s")
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="modified_%(class)s")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = get_current_user()
        if not self.pk:  # Object is being created
            self.created_by = user
        self.modified_by = user  # Always update modified_by
        super().save(*args, **kwargs)

class ApiKey(TrackingModel):
    name = models.CharField(max_length=255, help_text="Name of the API key owner or system", unique=True)
    key = models.CharField(max_length=64, unique=True, editable=False, help_text="Unique API key")
    is_active = models.BooleanField(default=True, help_text="Is the key active?")
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Expiration date of the key (optional)")
    allowed_ip_address = models.GenericIPAddressField(null=True, blank=True,
                                                      help_text="Allowed IP address for the API key")
    allowed_domain = models.CharField(max_length=255, null=True, blank=True, help_text="Allowed domain for the API key")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_hex(32)  # Generate a 64-character unique API key

        if self._state.adding:  # This checks if the instance is being created
            self.is_active = True

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {'Active' if self.is_active else 'Inactive'}"

    def is_valid(self, client_ip):
        """Check if the API key is active, not expired, and accessed from the allowed IP and domain."""
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False

        # Validate IP address if provided
        if self.allowed_ip_address:
            if self.allowed_ip_address != client_ip:
                return False

        # Additional validation for allowed domain if necessary
        return True
