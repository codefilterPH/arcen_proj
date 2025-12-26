from django.db import models
from django.utils import timezone
from student.models import Student
from schools.models import SchoolOrg, SchoolYear, Semester, Class, Flight
from django.core.exceptions import ValidationError

class Attendance(models.Model):
    STATUS_CHOICES = [
        ("PRESENT", "Present"),
        ("ABSENT", "Absent"),
        ("LATE", "Late"),
        ("EXCUSED", "Excused"),
        ("DISMISSED", "Dismissed"),
    ]

    # =========================
    # CONTEXT (NEW)
    # =========================

    school = models.ForeignKey(
        SchoolOrg,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    school_year = models.ForeignKey(
        SchoolYear,
        on_delete=models.CASCADE,
        related_name="attendance_records",
        null=True,
        blank=True
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name="attendance_records",
        null=True,
        blank=True
    )

    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="attendance_records",
        null=True,
        blank=True
    )

    flight = models.ForeignKey(
        Flight,
        on_delete=models.SET_NULL,
        related_name="attendance_records",
        null=True,
        blank=True
    )

    # =========================
    # STUDENT
    # =========================

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    # =========================
    # DATE + TIME
    # =========================

    date = models.DateField(default=timezone.now)
    time_in = models.TimeField(blank=True, null=True)
    time_out = models.TimeField(blank=True, null=True)

    # =========================
    # STATUS
    # =========================

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    # =========================
    # META
    # =========================

    class Meta:
        unique_together = ("student", "date", "class_obj")
        ordering = ["-date", "student__user__last_name"]

    # =========================
    # VALIDATION (IMPORTANT)
    # =========================

    def clean(self):
        if self.class_obj and self.semester:
            if self.class_obj.semester != self.semester:
                raise ValidationError("Class does not belong to the selected semester.")

        if self.flight and self.class_obj:
            if self.flight.class_obj != self.class_obj:
                raise ValidationError("Flight does not belong to the selected class.")

        if self.student and hasattr(self.student, "school"):
            if self.student.school != self.school:
                raise ValidationError("Student does not belong to this school.")

    def __str__(self):
        return (
            f"{self.school} | {self.class_obj} | "
            f"{self.student} | {self.date} | {self.status}"
        )

