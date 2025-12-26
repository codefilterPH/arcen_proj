from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image
from django.conf import settings
import qrcode
import io, base64, random
import os

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

    ENROLLMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('enrolled', 'Enrolled'),
        ('on_leave', 'On Leave'),
        ('graduated', 'Graduated'),
        ('transferred', 'Transferred'),
        ('dropped', 'Dropped'),
    ]

    # 🔹 Core Relations
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    school = models.ForeignKey(SchoolOrg, on_delete=models.CASCADE, related_name="students")

    # 🔹 Identification
    student_id = models.CharField(max_length=50, unique=True)
    qr_code = models.TextField(blank=True, null=True)

    # 🔹 Personal Info
    # 🔹 Legal / Recorded Identity (fixed at enrollment)
    rank = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150)
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150)
    extension_name = models.CharField(max_length=20, blank=True, null=True)

    email = models.EmailField(
        help_text="Recorded email at the time of enrollment."
    )
    preferred_initial = models.CharField(max_length=10, blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True, null=True, choices=GENDER_CHOICES)
    birth_date = models.DateField(blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    email_verified = models.BooleanField(default=False)

    enrollment_status = models.CharField(
        max_length=20,
        choices=ENROLLMENT_STATUS_CHOICES,
        default='pending',
        help_text="Current enrollment status of the student."
    )
    enrolled_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp when the student was officially enrolled."
    )
    status_changed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Last time enrollment status was changed."
    )

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
    is_active = models.BooleanField(
        default=True,
        help_text="Controls whether the student is active in the system."
    )

    # -------------------------------
    # Utility Methods
    # -------------------------------

    def generate_qr_code(self, force=False):
        """Generate or refresh QR code as Base64 PNG string with AFRC logo in center."""
        if self.qr_code and not force:
            return

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # REQUIRED for logo
            box_size=8,
            border=4,
        )

        qr.add_data(f"SCHOOL-{self.school_id}-STUDENT-{self.student_id}")
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

        # 🔹 Load AFRC logo
        logo_path = os.path.join(
            settings.BASE_DIR,
            "authentication",
            "static",
            "img",
            "afrc_brand.png"
        )

        if os.path.exists(logo_path):
            logo = Image.open(logo_path).convert("RGBA")

            # 🔹 Resize logo (max 25% of QR)
            qr_width, qr_height = qr_img.size
            logo_size = int(qr_width * 0.25)
            logo.thumbnail((logo_size, logo_size), Image.LANCZOS)

            # 🔹 Center logo
            pos = (
                (qr_width - logo.width) // 2,
                (qr_height - logo.height) // 2,
            )

            qr_img.paste(logo, pos, logo)

        # 🔹 Convert to Base64 PNG
        buffer = io.BytesIO()
        qr_img.save(buffer, format="PNG")
        self.qr_code = base64.b64encode(buffer.getvalue()).decode("utf-8")
        buffer.close()

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
        is_new = self.pk is None

        if not is_new:
            previous = Student.objects.filter(pk=self.pk).only(
                "enrollment_status",
                "enrolled_at"
            ).first()
        else:
            previous = None

        # 🔹 Normalize preferred initial
        if self.preferred_initial:
            self.preferred_initial = self.preferred_initial.upper()

        # 🔹 Detect enrollment status change
        if previous and previous.enrollment_status != self.enrollment_status:
            self.status_changed_at = timezone.now()

            # 🔹 First time officially enrolled
            if self.enrollment_status == "enrolled" and not previous.enrolled_at:
                self.enrolled_at = timezone.now()

        super().save(*args, **kwargs)

        # 🔹 QR generation
        if not self.qr_code:
            self.generate_qr_code()
            super().save(update_fields=["qr_code"])

    def __str__(self):
        full_name = " ".join(
            p for p in [
                self.rank,
                self.first_name,
                self.middle_name or "",
                self.last_name
            ] if p
        ).strip()

        fmt = (self.display_name_format or "title").lower()

        if fmt == "camel":
            return "".join(w.capitalize() for w in full_name.split())
        elif fmt == "upper":
            return full_name.upper()
        elif fmt == "lower":
            return full_name.lower()

        return full_name.title()


class FlightMembership(models.Model):
    """Students belong to a flight."""
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="memberships")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="flights")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("flight", "student")

    def __str__(self):
        return f"{self.student} → {self.flight}"
