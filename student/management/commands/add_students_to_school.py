import os
import json
import pandas as pd
from openpyxl.utils import column_index_from_string
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.conf import settings
from schools.models import SchoolOrg  # adjust if needed
from student.models import Student   # adjust if needed


class Command(BaseCommand):
    help = "🎓 Import and link students to schools from Excel using dynamic JSON settings"

    def handle(self, *args, **options):
        # ============================================================
        # 1️⃣ Ask for JSON settings file path (or default)
        # ============================================================
        default_path = os.path.join(settings.BASE_DIR, 'student', 'static', 'data', 'student_import_settings.json')
        self.stdout.write(self.style.NOTICE(f"Default settings: {default_path}"))
        user_input = input("Enter path to JSON settings (or press Enter for default): ").strip()
        config_path = user_input or default_path

        if not os.path.exists(config_path):
            raise CommandError(f"⚠️ JSON settings not found: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        filepath = config.get('filepath')
        sheetname = config.get('sheetname', 'Sheet1')
        col_map = config.get('mapping', {})

        if not filepath:
            raise CommandError("⚠️ Missing 'filepath' in settings.")
        if not col_map:
            raise CommandError("⚠️ 'mapping' section is empty.")

        # ============================================================
        # 2️⃣ Ask for school name (interactive)
        # ============================================================
        school_name = input("\n🏫 Enter the school name to assign students to: ").strip()
        if not school_name:
            raise CommandError("❌ School name cannot be empty.")

        school, created_school = SchoolOrg.objects.get_or_create(
            name__iexact=school_name,
            defaults={'name': school_name}
        )
        if created_school:
            self.stdout.write(self.style.SUCCESS(f"✅ Created new SchoolOrg: {school_name}"))
        else:
            self.stdout.write(self.style.NOTICE(f"📘 Using existing SchoolOrg: {school_name}"))

        # ============================================================
        # 3️⃣ Load Excel
        # ============================================================
        excel_path = os.path.join(settings.BASE_DIR, 'users', 'static', filepath)
        if not os.path.exists(excel_path):
            raise CommandError(f"❌ Excel file not found: {excel_path}")

        df = pd.read_excel(excel_path, sheet_name=sheetname, header=None)
        self.stdout.write(self.style.NOTICE(f"📂 Loaded {len(df)} rows from '{sheetname}'."))

        added, skipped, updated = 0, 0, 0

        # ============================================================
        # 4️⃣ Iterate and add students
        # ============================================================
        for idx, row in df.iterrows():
            try:
                first_name = str(row.iloc[column_index_from_string(col_map.get('first_name', 'E')) - 1]).strip()
                last_name = str(row.iloc[column_index_from_string(col_map.get('last_name', 'D')) - 1]).strip()

                if not first_name or not last_name:
                    continue

                # Match existing user
                user = User.objects.filter(first_name__iexact=first_name, last_name__iexact=last_name).first()

                if not user:
                    self.stdout.write(self.style.WARNING(f"⚠️ Row {idx+1}: No matching User for {first_name} {last_name}"))
                    skipped += 1
                    continue

                # Add or update Student record
                student, created = Student.objects.get_or_create(
                    user=user,
                    defaults={
                        "school": school,
                        "student_id": f"{school.id}-{user.id:05d}",
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"🆕 Added {first_name} {last_name} → {school.name}"))
                    added += 1
                elif student.school_id != school.id:
                    student.school = school
                    student.save(update_fields=['school'])
                    self.stdout.write(self.style.SUCCESS(f"🔄 Updated {first_name} {last_name} → {school.name}"))
                    updated += 1
                else:
                    self.stdout.write(self.style.WARNING(f"⏩ Already linked: {first_name} {last_name}"))
                    skipped += 1

            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️ Row {idx+1}: Error — {e}"))
                skipped += 1

        # ============================================================
        # ✅ Summary
        # ============================================================
        self.stdout.write(self.style.SUCCESS(
            f"🎯 Done — {added} added, {updated} updated, {skipped} skipped."
        ))
