from auditlog.registry import auditlog
from schools.models import SchoolOrg

auditlog.register(SchoolOrg)