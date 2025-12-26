import sys
import getpass
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from schools.models import SchoolOrg
from student.models import Student


class Command(BaseCommand):
    help = "🧹 Clear student records (all or per school) — PASSWORD REQUIRED"

    def add_arguments(self, parser):
        parser.add_argument(
            "--school",
            type=str,
            help="School name to clear students from (case-insensitive). If omitted, ALL students will be cleared.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview how many students would be deleted without actually deleting.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Skip YES confirmation (password is STILL required).",
        )
        parser.add_argument(
            "--username",
            type=str,
            help="Admin username (recommended). If omitted, you will be prompted.",
        )

    # ------------------------------------------------------------------
    # 🔐 Password Verification
    # ------------------------------------------------------------------
    def verify_password(self, username: str):
        self.stdout.write(self.style.WARNING("\n🔐 Authentication required"))
        password = getpass.getpass("Enter password: ")

        user = authenticate(username=username, password=password)
        if not user:
            raise CommandError("❌ Authentication failed. Invalid username or password.")

        if not user.is_staff and not user.is_superuser:
            raise CommandError("❌ Permission denied. Admin privileges required.")

        self.stdout.write(self.style.SUCCESS(f"✅ Authenticated as {user.username}"))
        return user

    # ------------------------------------------------------------------
    # 🚀 Main handler
    # ------------------------------------------------------------------
    def handle(self, *args, **options):
        school_name = options.get("school")
        dry_run = options.get("dry_run")
        force = options.get("force")
        username = options.get("username")

        # ------------------------------------------------------------
        # Ask username if missing
        # ------------------------------------------------------------
        if not username:
            username = input("Admin username: ").strip()
            if not username:
                raise CommandError("❌ Username is required.")

        # ------------------------------------------------------------
        # 🔐 Verify credentials FIRST
        # ------------------------------------------------------------
        self.verify_password(username)

        # ------------------------------------------------------------
        # Determine queryset
        # ------------------------------------------------------------
        if school_name:
            school = SchoolOrg.objects.filter(name__iexact=school_name).first()
            if not school:
                raise CommandError(f"❌ School not found: {school_name}")

            queryset = Student.objects.filter(school=school)
            scope_label = f"school '{school.name}'"
        else:
            queryset = Student.objects.all()
            scope_label = "ALL schools"

        total = queryset.count()

        if total == 0:
            self.stdout.write(self.style.WARNING("⚠️ No students found to delete."))
            return

        # ------------------------------------------------------------
        # Dry-run mode
        # ------------------------------------------------------------
        if dry_run:
            self.stdout.write(self.style.NOTICE(
                f"🧪 DRY RUN — {total} student(s) WOULD be deleted from {scope_label}."
            ))
            return

        # ------------------------------------------------------------
        # Confirmation
        # ------------------------------------------------------------
        if not force:
            self.stdout.write(self.style.WARNING(
                f"\n⚠️ You are about to DELETE {total} student(s) from {scope_label}."
            ))
            self.stdout.write(self.style.WARNING("❗ This action CANNOT be undone.\n"))

            confirm = input("Type YES to confirm deletion: ").strip()
            if confirm != "YES":
                self.stdout.write(self.style.NOTICE("❎ Operation cancelled."))
                sys.exit(0)

        # ------------------------------------------------------------
        # Execute deletion
        # ------------------------------------------------------------
        with transaction.atomic():
            deleted_count, _ = queryset.delete()

        self.stdout.write(self.style.SUCCESS(
            f"✅ Successfully deleted {deleted_count} student record(s) from {scope_label}."
        ))
