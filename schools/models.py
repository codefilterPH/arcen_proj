from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from auditlog.registry import auditlog
from django.utils.text import slugify

class SchoolOrg(models.Model):
    """A school or organization that admits students."""
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, blank=True, null=True)

    address = models.TextField(blank=True, null=True)
    logo = models.ImageField(
        upload_to="schools/logos/",
        blank=True,
        null=True,
        help_text="Upload the logo of the school (optional)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        base_slug = slugify(self.name)
        new_slug = base_slug
        counter = 1

        # Only regenerate if slug is empty OR name changed
        if not self.slug or self.slug != base_slug:
            while SchoolOrg.objects.filter(slug=new_slug).exclude(pk=self.pk).exists():
                new_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = new_slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class SchoolYear(models.Model):
    """School year, e.g., 2025-2026."""
    school = models.ForeignKey(
        SchoolOrg,
        on_delete=models.CASCADE,
        related_name="school_years"
    )
    name = models.CharField(max_length=20, help_text="Example: 2025-2026")
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        verbose_name = "School Year"
        verbose_name_plural = "School Years"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.school.name} - {self.name}"

class Semester(models.Model):
    """Each school year is divided into semesters."""
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, related_name="semesters")
    name = models.CharField(max_length=50)  # e.g., "1st Semester", "2nd Semester"
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.school_year.name} - {self.name}"


class Class(models.Model):
    """Each semester contains classes."""
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name="classes")
    name = models.CharField(max_length=100)  # e.g., "Math 101"
    code = models.CharField(max_length=20, unique=True)
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Flight(models.Model):
    """A class can be divided into multiple flights (sections)."""
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="flights")
    name = models.CharField(max_length=50)  # e.g., "Alpha Flight", "Bravo Flight"

    def __str__(self):
        return f"{self.class_obj.code} - {self.name}"


