# users/management/commands/load_designations.py
from django.core.management.base import BaseCommand
from users.models import Designation

class Command(BaseCommand):
    help = "Load default designations into the Designation model"

    DEFAULT_DESIGNATIONS = [
        "Chairperson",
        "Vice-Chairperson",
        "Member",
        "Treasurer",
        "Secretary",
        "Asst. Secretary",
        "Resource Person (Internal Auditor)",
        "Secretary (Non-voting)",
        "Ex-Officio Member (Non-voting)",
        "Resource Person (Chief, HRMS)",
        "Researcher",
        "Member (VP Finance)",
        "Resource Person (VP for IT/MIS)",
        "Resource Person (Project Mgmt. Lead)",
        "Resource Person (VP for MMCD)",
        "Resource Person (Risk Mgmt Officer)",
        "Resource Person (Compliance Officer)",
        "Resource Person; PCEO",
        "Resource Person; Internal Auditor",
    ]

    def handle(self, *args, **options):
        created_count = 0
        for name in self.DEFAULT_DESIGNATIONS:
            obj, created = Designation.objects.get_or_create(name=name)
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Inserted {created_count} new designations (others already existed).")
        )
