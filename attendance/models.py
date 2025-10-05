from django.db import models
from schools.models import Flight
from student.models import Student

# Create your models here.
class Attendance(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ("PRESENT", "Present"),
        ("ABSENT", "Absent"),
        ("LATE", "Late"),
        ("EXCUSED", "Excused"),
    ])

    class Meta:
        unique_together = ("flight", "student", "date")

    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"
