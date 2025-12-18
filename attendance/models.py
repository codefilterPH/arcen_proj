from django.db import models
from django.utils import timezone
from student.models import Student


class Attendance(models.Model):
    STATUS_CHOICES = [
        ("PRESENT", "Present"),
        ("ABSENT", "Absent"),
        ("LATE", "Late"),
        ("EXCUSED", "Excused"),
        ("DISMISSED", "Dismissed"),
    ]

    # 🔹 Required relation
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    # 🔹 Date + time
    date = models.DateField(default=timezone.now)
    time_in = models.TimeField(blank=True, null=True)
    time_out = models.TimeField(blank=True, null=True)

    # 🔹 Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ("student", "date")   # 👈 Only one attendance per student per day
        ordering = ["-date", "student__user__last_name"]

    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"
