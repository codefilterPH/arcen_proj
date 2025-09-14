from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import random

# Create your models here.
class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    CLASSIFICATION_CHOICES = [
        ('OFFICER', 'Officer'),
        ('ENLISTED', 'Enlisted Personnel'),
        ('CIVILIAN', 'Civilian'),
        ('OTHERS', 'Others'),
    ]

    DISPLAY_NAME_CHOICES = [
        ('title', 'Title Case (John De La Cruz)'),
        ('camel', 'Upper Camel Case (JohnDeLaCruz)'),
        ('upper', 'UPPERCASE (JOHN DE LA CRUZ)'),
        ('lower', 'lowercase (john de la cruz)'),
    ]

    objects = None
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    afpsn = models.CharField(max_length=100, blank=True, null=True)
    rank = models.CharField(max_length=100, blank=True, null=True)
    classification = models.CharField(max_length=100, blank=True, null=True, choices=CLASSIFICATION_CHOICES,)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    preferred_initial = models.CharField(max_length=10, blank=True, null=True)
    extension_name = models.CharField(max_length=10, blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True, null=True, choices=GENDER_CHOICES)
    birth_date = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    default_avatar = models.CharField(max_length=255, blank=True, null=True)
    signature = models.TextField(blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=11, blank=True, null=True)
    last_activity = models.DateTimeField(default=timezone.now)
    last_password_reset = models.DateTimeField(default=timezone.now)
    position = models.CharField(max_length=50, blank=True, null=True)
    password_reset_expiration = models.DateTimeField(null=True, blank=True)
    display_name_format = models.CharField(
        max_length=20,
        choices=DISPLAY_NAME_CHOICES,
        default='title',
        help_text="Controls how the user's display name is formatted"
    )

    def save(self, *args, **kwargs):
        # Convert preferred_initial to uppercase before saving
        if self.preferred_initial:
            self.preferred_initial = self.preferred_initial.upper()

        super(UserProfile, self).save(*args, **kwargs)

    @property
    def get_profile_picture_url(self):
        # 1. Check if the user has uploaded a profile picture
        if self.profile_picture:
            return self.profile_picture.url

        # 2. Check if a default avatar is assigned
        if self.default_avatar:
            return f'/static/img/users/avatars/{self.default_avatar}'

        # 3. If no profile picture and no default avatar, assign one
        avatar_images = [
            'bear.png', 'cat.png', 'duck.png', 'gorilla.png',
            'koala.png', 'panda.png', 'sea-lion.png', 'jaguar.png', 'dog.png',
        ]
        self.default_avatar = random.choice(avatar_images)
        self.save()  # Save the default avatar to the model

        # 4. Return the path for the newly assigned default avatar
        return f'/static/img/users/avatars/{self.default_avatar}'

    def __str__(self):
        # Handle AFP Serial Number (afpsn) with classification check
        afpsn_display = ""
        if self.afpsn:
            afpsn_display = (
                f"O-{self.afpsn}"
                if self.classification and self.classification.upper() == "OFFICER"
                else self.afpsn
            )

        # Build the core name parts
        first_name = self.user.first_name or ""
        last_name = self.user.last_name or ""
        full_name = " ".join(p for p in [first_name, last_name] if p).strip()

        # Always include rank if exists
        rank_display = self.rank or ""

        # Default base display
        base_display = " ".join(
            part for part in [rank_display, full_name.title(), afpsn_display] if part
        ).strip()

        # If no display_name_format → return normal formatting
        if not self.display_name_format:
            return base_display

        # Apply formatting rules
        fmt = self.display_name_format.lower()

        if fmt == "camel":
            # Upper Camel Case: JohnDeLaCruz
            name_fmt = "".join(w.capitalize() for w in full_name.split())
            return " ".join(part for part in [rank_display, name_fmt, afpsn_display] if part).strip()

        elif fmt == "upper":
            return " ".join(
                part for part in [rank_display.upper(), full_name.upper(), afpsn_display] if part
            ).strip()

        elif fmt == "lower":
            return " ".join(
                part for part in [rank_display.lower(), full_name.lower(), afpsn_display] if part
            ).strip()

        elif fmt == "title":
            return base_display

        # Fallback
        return base_display

