import os
import json
import pandas as pd
from datetime import datetime
from openpyxl.utils import column_index_from_string

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone

from schools.models import SchoolOrg
from student.models import Student


# ============================================================
# 🧹 Helper: Contact Number Cleaner
# ============================================================
def clean_contact_number(raw_value):
    if not raw_value or pd.isna(raw_value):
        return None

    val = str(raw_value).strip()
    val = val.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

    if val.startswith("+63"):
        val = "0" + val[3:]
    elif val.startswith("63"):
        val = "0" + val[2:]

    val = "".join(c for c in val if c.isdigit())

    if len(val) > 11:
        val = val[-11:]

    return val


# ============================================================
# 🕒 Helper: Date Parser
# ============================================================
def parse_excel_date(value):
    if pd.isna(value):
        return None

    if isinstance(value, (float, int)) and value > 40000:
        try:
            return pd.to_datetime(value, origin="1899-12-30", unit="D")
        except Exception:
            return None

    if isinstance(value, str):
        value = value.strip()
        for fmt in [
            "%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y",
            "%m-%d-%Y", "%m/%d/%y", "%m-%d-%y"
        ]:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue

        try:
            parsed = pd.to_datetime(value, errors="coerce")
            if parsed is not pd.NaT and parsed.year >= 1900:
                return parsed
        except Exception:
            return None

    if isinstance(value, pd.Timestamp):
        return value

    return None


# ============================================================
# 📥 Django Command
# ============================================================
class Command(BaseCommand):
    help = "📥 Import users from Excel and auto-enroll them into a specific school"

    def add_arguments(self, parser):
        parser.add_argument(
            "--school-id",
            type=int,
            required=True,
            help="Target SchoolOrg ID for enrollment"
        )

    def handle(self, *args, **options):
        school_id = options["school_id"]

        # ------------------------------------------------------------
        # 🔎 Validate School
        # ------------------------------------------------------------
        try:
            school = SchoolOrg.objects.get(pk=school_id)
        except SchoolOrg.DoesNotExist:
            raise CommandError(f"❌ School with ID {school_id} does not exist")

        self.stdout.write(self.style.SUCCESS(
            f"🏫 Enrolling students into: {school.name}"
        ))

        # ------------------------------------------------------------
        # 📄 Load Config
        # ------------------------------------------------------------
        config_path = os.path.join(
            settings.BASE_DIR,
            "users",
            "static",
            "data",
            "user_import_settings.json"
        )

        if not os.path.exists(config_path):
            raise CommandError("❌ Import config JSON not found")

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        filepath = config.get("filepath")
        sheetname = config.get("sheetname", "Sheet1")
        col_map = config.get("mapping", {})
        default_password = config.get("default_password", "ChangeMe123!")

        if not filepath or not col_map:
            raise CommandError("❌ Invalid import config")

        excel_path = os.path.join(settings.BASE_DIR, "users", "static", filepath)
        if not os.path.exists(excel_path):
            raise CommandError(f"❌ Excel file not found: {excel_path}")

        # ------------------------------------------------------------
        # 📊 Load Excel
        # ------------------------------------------------------------
        df = pd.read_excel(excel_path, sheet_name=sheetname, header=None)

        self.stdout.write(self.style.NOTICE(
            f"📄 Loaded sheet '{sheetname}' with {len(df)} rows"
        ))

        created_users = 0
        created_students = 0
        updated_students = 0

        # ------------------------------------------------------------
        # 🔁 Iterate Rows
        # ------------------------------------------------------------
        for idx, row in df.iterrows():
            self.stdout.write(
                self.style.NOTICE(f"\n➡️ Processing row {idx + 1}")
            )

            # ------------------------------
            # 🔑 Username Resolution
            # ------------------------------
            username = ""
            email = ""

            if "username" in col_map:
                try:
                    username = str(
                        row.iloc[column_index_from_string(col_map["username"]) - 1]
                    ).strip()
                except Exception:
                    pass

            if not username and "email" in col_map:
                email = str(
                    row.iloc[column_index_from_string(col_map["email"]) - 1]
                ).strip().lower()
                username = email

            if not username:
                username = f"imported_user_{idx + 1:06d}"
                self.stdout.write(self.style.WARNING(
                    f"⚠️ No username/email found → generated '{username}'"
                ))

            # ------------------------------
            # 👤 Auth User (GLOBAL)
            # ------------------------------
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={"email": email}
            )

            if user_created:
                user.set_password(default_password)
                user.save()
                created_users += 1
                self.stdout.write(
                    self.style.SUCCESS(f"👤 Created auth user: {username}")
                )
            else:
                self.stdout.write(
                    self.style.NOTICE(f"👤 Reused auth user: {username}")
                )

            # ------------------------------
            # 🎓 Student (PER SCHOOL)
            # ------------------------------
            student, created = Student.objects.get_or_create(
                user=user,
                school=school,
                defaults={
                    "student_id": f"{school.slug.upper()}-{user.id}",
                    "email": email,
                    "enrollment_status": "pending",
                    "enrolled_at": timezone.now(),
                }
            )

            if created:
                created_students += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"🎓 Enrolled NEW student → {username} @ {school.name}"
                    )
                )
            else:
                updated_students += 1
                self.stdout.write(
                    self.style.NOTICE(
                        f"🎓 Updated EXISTING student → {username} @ {school.name}"
                    )
                )

            # ------------------------------
            # 🧩 SAFE FIELD MAPPING
            # ------------------------------
            SKIP_FIELDS = {
                "username", "email",
                "user", "school",
                "student_id",
                "enrollment_status",
                "enrolled_at"
            }

            for field, col_letter in col_map.items():
                if field in SKIP_FIELDS or not hasattr(student, field):
                    continue

                try:
                    value = row.iloc[column_index_from_string(col_letter) - 1]
                except Exception:
                    continue

                if pd.isna(value):
                    continue

                original = getattr(student, field, None)

                if field == "contact_number":
                    value = clean_contact_number(value)

                if field == "birth_date":
                    value = parse_excel_date(value)

                if original != value:
                    setattr(student, field, value)
                    self.stdout.write(
                        self.style.NOTICE(
                            f"   • {field}: '{original}' → '{value}'"
                        )
                    )

            student.save()

        # ------------------------------------------------------------
        # ✅ Summary
        # ------------------------------------------------------------
        self.stdout.write(self.style.SUCCESS(
            f"""
✅ IMPORT COMPLETE
• Auth users created: {created_users}
• Students enrolled: {created_students}
• Students updated: {updated_students}
• School: {school.name}
"""
        ))
