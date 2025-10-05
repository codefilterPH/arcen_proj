from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
import qrcode
import io, base64, random

from schools.models import SchoolOrg, Flight
from users.models import Designation, Classification  # ✅ Adjust import paths to your project structure


class Student(models.Model):
    """A student enrolled under a school organization."""
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

    # 🔹 Core Relations
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    school = models.ForeignKey(SchoolOrg, on_delete=models.CASCADE, related_name="students")

    # 🔹 Identification
    student_id = models.CharField(max_length=50, unique=True)
    qr_code = models.TextField(blank=True, null=True)

    # 🔹 Personal Info
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    preferred_initial = models.CharField(max_length=10, blank=True, null=True)
    extension_name = models.CharField(max_length=10, blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True, null=True, choices=GENDER_CHOICES)
    birth_date = models.DateField(blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    email_verified = models.BooleanField(default=False)

    # 🔹 Academic & Organizational Info
    designations = models.ManyToManyField(Designation, blank=True)
    classification = models.ForeignKey(
        Classification,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="students"
    )

    # 🔹 Visual Representation
    profile_picture = models.ImageField(upload_to='students/profile_pics/', blank=True, null=True)
    default_avatar = models.CharField(max_length=255, blank=True, null=True)
    display_name_format = models.CharField(
        max_length=20,
        choices=DISPLAY_NAME_CHOICES,
        default='title',
        help_text="Controls how the student's name is displayed."
    )

    # 🔹 Timestamps
    joined_date = models.DateField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    # -------------------------------
    # Utility Methods
    # -------------------------------

    def generate_qr_code(self, force=False):
        """Generate or refresh QR code as Base64 PNG string."""
        if self.qr_code and not force:
            return

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=8,
            border=4,
        )
        qr.add_data(f"STUDENT-{self.student_id}")
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        base64_qr = base64.b64encode(buffer.getvalue()).decode("utf-8")
        buffer.close()

        self.qr_code = base64_qr

    def get_profile_picture_url(self):
        """Returns student's profile or default avatar URL."""
        if self.profile_picture:
            return self.profile_picture.url
        if self.default_avatar:
            return f"/static/img/users/avatars/{self.default_avatar}"

        avatar_images = [
            'bear.png', 'cat.png', 'duck.png', 'gorilla.png',
            'koala.png', 'panda.png', 'sea-lion.png', 'jaguar.png', 'dog.png',
        ]
        selected_avatar = random.choice(avatar_images)
        self.default_avatar = selected_avatar
        self.save(update_fields=["default_avatar"])
        return f"/static/img/users/avatars/{self.default_avatar}"

    def save(self, *args, **kwargs):
        if self.preferred_initial:
            self.preferred_initial = self.preferred_initial.upper()
        super().save(*args, **kwargs)
        if not self.qr_code:
            self.generate_qr_code()
            super().save(update_fields=["qr_code"])

    def __str__(self):
        """Custom display based on selected format."""
        first_name = self.user.first_name or ""
        last_name = self.user.last_name or ""
        full_name = " ".join(p for p in [first_name, self.middle_name or "", last_name] if p).strip()
        rank_display = ""
        base_display = " ".join(part for part in [rank_display, full_name.title()] if part).strip()

        fmt = self.display_name_format.lower() if self.display_name_format else "title"
        if fmt == "camel":
            name_fmt = "".join(w.capitalize() for w in full_name.split())
            return name_fmt
        elif fmt == "upper":
            return full_name.upper()
        elif fmt == "lower":
            return full_name.lower()
        return base_display

class FlightMembership(models.Model):
    """Students belong to a flight."""
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="memberships")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="flights")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("flight", "student")

    def __str__(self):
        return f"{self.student} → {self.flight}"
