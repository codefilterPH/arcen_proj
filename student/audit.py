from auditlog.registry import auditlog
from student.models import Student

auditlog.register(Student)