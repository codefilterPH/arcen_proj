import os
import json
import pandas as pd
from datetime import datetime
from openpyxl.utils import column_index_from_string
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.conf import settings
from users.models import UserProfile


# ============================================================
# 🧹 Helper: Contact Number Cleaner
# ============================================================
def clean_contact_number(raw_value):
    """Normalize contact numbers: convert +63 or 63 to 0, remove non-digits."""
    if not raw_value or pd.isna(raw_value):
        return None

    val = str(raw_value).strip()
    val = val.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

    # Replace +63 and 63 at the beginning with 0
    if val.startswith("+63"):
        val = "0" + val[3:]
    elif val.startswith("63"):
        val = "0" + val[2:]

    # Keep only digits
    val = "".join(c for c in val if c.isdigit())

    # If still longer than 11, keep last 11 digits
    if len(val) > 11:
        val = val[-11:]

    return val


# ============================================================
# 🕒 Helper: Date Parser
# ============================================================
def parse_excel_date(value):
    """Try to safely convert Excel date or string to a proper datetime."""
    if pd.isna(value):
        return None

    # Excel serial date numbers (e.g., 45382)
    if isinstance(value, (float, int)) and value > 40000:
        try:
            return pd.to_datetime(value, origin='1899-12-30', unit='D')
        except Exception:
            return None

    # Common string formats
    if isinstance(value, str):
        value = value.strip()
        common_formats = [
            "%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y",
            "%m-%d-%Y", "%m/%d/%y", "%m-%d-%y"
        ]
        for fmt in common_formats:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue

        # Excel sometimes outputs weird small years like '6/28/0005' — skip them
        try:
            date_candidate = pd.to_datetime(value, errors='coerce')
            if date_candidate is not pd.NaT and date_candidate.year >= 1900:
                return date_candidate
            return None
        except Exception:
            return None

    # Already a pandas Timestamp or datetime
    if isinstance(value, pd.Timestamp):
        return value

    return None


# ============================================================
# 📥 Django Command
# ============================================================
class Command(BaseCommand):
    help = "📥 Import users and profiles from Excel using static JSON settings (no headers required)"

    def handle(self, *args, **options):
        # 1️⃣ Load configuration
        config_path = os.path.join(
            settings.BASE_DIR,
            'users',
            'static',
            'data',
            'user_import_settings.json'
        )

        if not os.path.exists(config_path):
            raise CommandError(f"Settings file not found at: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        filepath = config.get('filepath')
        sheetname = config.get('sheetname', 'Sheet1')
        col_map = config.get('mapping', {})

        if not filepath:
            raise CommandError("⚠️ 'filepath' is missing in settings JSON.")
        if not col_map:
            raise CommandError("⚠️ 'mapping' is empty in JSON settings.")

        excel_path = os.path.join(settings.BASE_DIR, 'users', 'static', filepath)
        if not os.path.exists(excel_path):
            raise CommandError(f"Excel file not found: {excel_path}")

        # 2️⃣ Load Excel
        df = pd.read_excel(excel_path, sheet_name=sheetname, header=None)
        self.stdout.write(self.style.NOTICE(
            f"Loaded '{sheetname}' with {len(df)} rows (no headers)."
        ))

        created, updated = 0, 0

        # 3️⃣ Iterate rows
        for idx, row in df.iterrows():

            # ------------------------------------------------------------
            # 🔑 USERNAME RESOLUTION (UNCHANGED)
            # ------------------------------------------------------------
            username = ""

            if 'username' in col_map:
                try:
                    username = str(
                        row.iloc[column_index_from_string(col_map['username']) - 1]
                    ).strip()
                except Exception:
                    username = ""

            email = ""
            if not username and 'email' in col_map:
                try:
                    email = str(
                        row.iloc[column_index_from_string(col_map['email']) - 1]
                    ).strip().lower()
                    username = email
                except Exception:
                    pass

            if not username:
                username = f"imported_user_{idx + 1:06d}"
                self.stdout.write(self.style.WARNING(
                    f"⚠️ Row {idx + 1}: Generated username '{username}'"
                ))

            if not email:
                email = str(
                    row.iloc[column_index_from_string(col_map.get('email', 'B')) - 1]
                ).strip().lower()

            first_name = str(
                row.iloc[column_index_from_string(col_map.get('first_name', 'C')) - 1]
            ).strip()

            last_name = str(
                row.iloc[column_index_from_string(col_map.get('last_name', 'D')) - 1]
            ).strip()

            # ------------------------------------------------------------
            # 👤 AUTH USER (REUSE IF EXISTS)
            # ------------------------------------------------------------
            user = User.objects.filter(username=username).first()

            if not user:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=config.get("default_password", "ChangeMe123!")
                )
                created += 1
                self.stdout.write(self.style.SUCCESS(
                    f"🆕 Created user: {username}"
                ))
            else:
                updated += 1

            # ------------------------------------------------------------
            # 👤 USER PROFILE (AUTO-ENROLL / UPDATE)
            # ------------------------------------------------------------
            profile, _ = UserProfile.objects.get_or_create(user=user)

            for field, col_letter in col_map.items():
                if field in ['username', 'email', 'first_name', 'last_name']:
                    continue

                try:
                    value = row.iloc[column_index_from_string(col_letter) - 1]

                    if pd.notna(value) and hasattr(profile, field):
                        parsed_val = parse_excel_date(value)

                        if isinstance(parsed_val, (datetime, pd.Timestamp)) and parsed_val.year < 1900:
                            continue

                        if isinstance(parsed_val, pd.Timestamp):
                            parsed_val = parsed_val.strftime('%Y-%m-%d')

                        val_str = str(parsed_val).strip()

                        if field == "contact_number":
                            val_str = clean_contact_number(val_str)

                        setattr(profile, field, val_str)

                except Exception as e:
                    self.stdout.write(self.style.WARNING(
                        f"⚠️ Row {idx + 1}: Field '{field}' skipped ({e})"
                    ))

            profile.save()

        # ✅ Summary
        self.stdout.write(self.style.SUCCESS(
            f"✅ Import completed — {created} users created, {updated} reused."
        ))