from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
import random
import qrcode
import io, base64
import json

class Designation(models.Model):
    """Represents an official designation/role a user can have."""

    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    address = models.TextField(blank=True)
    contact_person = models.CharField(max_length=255, blank=True)
    contact_number = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_organizations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Classification(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('N', 'Non-binary'),
        ('X', 'Prefer not to say'),
    ]
    DISPLAY_NAME_CHOICES = [
        ('title', 'Title Case (John De La Cruz)'),
        ('camel', 'Upper Camel Case (JohnDeLaCruz)'),
        ('upper', 'UPPERCASE (JOHN DE LA CRUZ)'),
        ('lower', 'lowercase (john de la cruz)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="userprofile")
    rank = models.CharField(max_length=100, blank=True, null=True)
    sub_svc = models.CharField(max_length=100, blank=True, null=True)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    preferred_initial = models.CharField(max_length=10, blank=True, null=True)
    extension_name = models.CharField(max_length=10, blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True, null=True, choices=GENDER_CHOICES)
    birth_date = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    default_avatar = models.CharField(max_length=255, blank=True, null=True)
    signature = models.TextField(blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)
    designations = models.ManyToManyField("Designation", blank=True)
    classification = models.ForeignKey(
        Classification,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="user_profiles"
    )

    email_verified = models.BooleanField(default=False)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    last_activity = models.DateTimeField(default=timezone.now)
    last_password_reset = models.DateTimeField(default=timezone.now)

    organizations = models.ManyToManyField(Organization, related_name="user_organizations", blank=True)
    default_organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="default_organization"
    )
    display_name_format = models.CharField(
        max_length=20,
        choices=DISPLAY_NAME_CHOICES,
        default='title',
        help_text="Controls how the user's display name is formatted"
    )
    qr_code = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True, verbose_name="Address")
    city = models.CharField(max_length=100, blank=True, null=True)
    province = models.CharField(max_length=250, blank=True, null=True)
    course = models.CharField(max_length=500, blank=True, null=True)

    def clean(self):
        """Ensure default organization is among assigned organizations."""
        if self.default_organization and not self.organizations.filter(id=self.default_organization.id).exists():
            raise ValidationError({
                "default_organization": "The default organization must be one of the assigned organizations."
            })

    def generate_qr_code(self, force=False):
        """Generate QR with JSON payload using AUTH USER ID but NO ORGANIZATION."""
        if self.qr_code and not force:
            return

        # Build profile picture URL
        if self.profile_picture:
            profile_pic_url = self.profile_picture.url
        else:
            profile_pic_url = (
                f"/static/img/users/avatars/{self.default_avatar}"
                if self.default_avatar else ""
            )

        # Build QR JSON payload (NO organization)
        qr_payload = {
            "user_id": self.user.id,  # 🔥 Django user ID
            "name": str(self),  # 🔥 formatted via __str__
            "rank": self.rank or "",
            "contact_number": self.contact_number or "",
            "address": self.address or "",
            "city": self.city or "",
            "province": self.province or "",
            "classification": (
                self.classification.name if self.classification else ""
            ),
            "profile_picture": profile_pic_url,  # 🔥 picture URL included
        }

        qr_text = json.dumps(qr_payload)

        # Create QR
        qr = qrcode.QRCode(
            version=4,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_text)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

        buffer = io.BytesIO()
        qr_img.save(buffer, format="PNG")
        base64_qr = base64.b64encode(buffer.getvalue()).decode("utf-8")
        buffer.close()

        self.qr_code = base64_qr

    def save(self, *args, **kwargs):

        # Normalize initials
        if self.preferred_initial:
            self.preferred_initial = self.preferred_initial.upper()

        # Detect if QR should be regenerated
        regenerate_qr = False

        if self.pk:
            old = UserProfile.objects.filter(pk=self.pk).first()

            # Check fields included in QR
            fields_to_watch = [
                "rank", "contact_number", "address",
                "city", "province", "default_avatar",
                "profile_picture", "classification_id",
                "display_name_format"
            ]

            for field in fields_to_watch:
                if getattr(old, field) != getattr(self, field):
                    regenerate_qr = True
                    break

            # Check user first/last name
            if old.user.first_name != self.user.first_name or old.user.last_name != self.user.last_name:
                regenerate_qr = True

        # Save the profile first
        super().save(*args, **kwargs)

        # Regenerate QR if needed
        if regenerate_qr or not self.qr_code:
            self.generate_qr_code(force=True)
            super().save(update_fields=["qr_code"])

    @property
    def get_profile_picture_url(self):
        print(f"Fetching profile picture URL for user profile ID: {self.id}")

        if self.profile_picture:
            print(f"User has uploaded a profile picture: {self.profile_picture.url}")
            return self.profile_picture.url

        if self.default_avatar:
            print(f"User already has a default avatar assigned: {self.default_avatar}")
            return f'/static/img/users/avatars/{self.default_avatar}'

        # Assign random avatar if none exists
        avatar_images = [
            'bear.png', 'cat.png', 'duck.png', 'gorilla.png',
            'koala.png', 'panda.png', 'sea-lion.png', 'jaguar.png', 'dog.png',
        ]
        selected_avatar = random.choice(avatar_images)
        self.default_avatar = selected_avatar
        self.save()
        print(f"No profile picture or avatar found. Assigned new random avatar: {selected_avatar}")

        return f'/static/img/users/avatars/{self.default_avatar}'

    def __str__(self):
        # Build the core name parts
        first_name = self.user.first_name or ""
        last_name = self.user.last_name or ""
        full_name = " ".join(p for p in [first_name, last_name] if p).strip()

        # Always include rank if exists
        rank_display = self.rank or ""

        # Default base display
        base_display = " ".join(
            part for part in [rank_display, full_name.title()] if part
        ).strip()

        # If no display_name_format → return normal formatting
        if not self.display_name_format:
            return base_display

        fmt = self.display_name_format.lower()

        if fmt == "camel":
            # Upper Camel Case: JohnDeLaCruz
            name_fmt = "".join(w.capitalize() for w in full_name.split())
            return " ".join(part for part in [rank_display, name_fmt] if part).strip()

        elif fmt == "upper":
            return " ".join(
                part for part in [rank_display.upper(), full_name.upper()] if part
            ).strip()

        elif fmt == "lower":
            return " ".join(
                part for part in [rank_display.lower(), full_name.lower()] if part
            ).strip()

        elif fmt == "title":
            return base_display

        # Fallback
        return base_display
