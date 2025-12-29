from django.core.management.base import BaseCommand, CommandError
from schools.models import SchoolOrg
from student.models import Student


class Command(BaseCommand):
    help = "🗑️ Permanently DELETE all students from a specific school (auth users untouched)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--school-id",
            type=int,
            required=True,
            help="Target SchoolOrg ID"
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview deletions without deleting"
        )

    def handle(self, *args, **options):
        school_id = options["school_id"]
        dry_run = options["dry_run"]

        # ------------------------------------------------------------
        # 🔎 Validate School
        # ------------------------------------------------------------
        try:
            school = SchoolOrg.objects.get(pk=school_id)
        except SchoolOrg.DoesNotExist:
            raise CommandError(f"❌ School with ID {school_id} does not exist")

        self.stdout.write(self.style.SUCCESS(
            f"🏫 Target school: {school.name}"
        ))

        # ------------------------------------------------------------
        # 🎓 Fetch Students
        # ------------------------------------------------------------
        students = Student.objects.filter(school=school)
        total = students.count()

        if total == 0:
            self.stdout.write(self.style.WARNING(
                "⚠️ No students found for this school"
            ))
            return

        self.stdout.write(self.style.NOTICE(
            f"📋 Found {total} students to DELETE"
        ))

        if dry_run:
            self.stdout.write(self.style.WARNING(
                "🧪 DRY-RUN MODE — nothing will be deleted"
            ))

        # ------------------------------------------------------------
        # 🔥 Delete Students
        # ------------------------------------------------------------
        deleted = 0

        for idx, student in enumerate(students, start=1):
            self.stdout.write(
                self.style.WARNING(
                    f"🗑️ [{idx}/{total}] Deleting: {student} "
                    f"(user={student.user.username})"
                )
            )

            if not dry_run:
                student.delete()

            deleted += 1

        # ------------------------------------------------------------
        # ✅ Summary
        # ------------------------------------------------------------
        self.stdout.write(self.style.SUCCESS(
            f"""
✅ DELETE COMPLETE
• School: {school.name}
• Students deleted: {deleted}
• Dry-run: {dry_run}
"""
        ))
