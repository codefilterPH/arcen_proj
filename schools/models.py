from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class SchoolOrg(models.Model):
    """A school or organization that admits students."""
    name = models.CharField(max_length=255, unique=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Student(models.Model):
    """A student who belongs to a school org."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ForeignKey(SchoolOrg, on_delete=models.CASCADE, related_name="students")
    student_id = models.CharField(max_length=50, unique=True)
    joined_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.student_id})"


class SchoolYear(models.Model):
    """Academic year, e.g., 2025-2026."""
    school = models.ForeignKey(SchoolOrg, on_delete=models.CASCADE, related_name="school_years")
    name = models.CharField(max_length=20)  # e.g., "2025-2026"
    start_date = models.DateField()
    end_date = models.DateField()

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


class FlightMembership(models.Model):
    """Students belong to a flight."""
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="memberships")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="flights")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("flight", "student")

    def __str__(self):
        return f"{self.student} → {self.flight}"
