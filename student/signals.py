from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from users.models import UserProfile
from student.models import Student


@receiver(post_save, sender=Student)
def sync_userprofile_to_student(sender, instance, created, **kwargs):
    """
    On FIRST creation of Student:
    - Snapshot UserProfile identity & contact fields
    - Copy visual + academic info
    - Initialize enrollment timestamps if applicable
    """

    # 🚫 Only run on creation (snapshot rule)
    if not created:
        return

    user = instance.user

    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        # Hard stop — student must still exist even without profile
        return

    update_fields = []

    # ============================================================
    # 🔹 SNAPSHOT IDENTITY (IMMUTABLE AFTER ENROLLMENT)
    # ============================================================
    instance.rank = profile.rank or ""
    instance.first_name = user.first_name or ""
    instance.middle_name = profile.middle_name
    instance.last_name = user.last_name or ""
    instance.extension_name = profile.extension_name
    instance.email = user.email or ""

    update_fields += [
        "rank",
        "first_name",
        "middle_name",
        "last_name",
        "extension_name",
        "email",
    ]

    # ============================================================
    # 🔹 PERSONAL / CONTACT INFO
    # ============================================================
    instance.gender = profile.gender
    instance.birth_date = profile.birth_date
    instance.contact_number = profile.contact_number
    instance.email_verified = profile.email_verified
    instance.preferred_initial = profile.preferred_initial

    update_fields += [
        "gender",
        "birth_date",
        "contact_number",
        "email_verified",
        "preferred_initial",
    ]

    # ============================================================
    # 🔹 VISUAL REPRESENTATION
    # ============================================================
    if profile.profile_picture:
        instance.profile_picture = profile.profile_picture
        update_fields.append("profile_picture")

    if profile.default_avatar:
        instance.default_avatar = profile.default_avatar
        update_fields.append("default_avatar")

    instance.display_name_format = profile.display_name_format
    update_fields.append("display_name_format")

    # ============================================================
    # 🔹 ACADEMIC / ORGANIZATIONAL
    # ============================================================
    instance.classification = profile.classification
    update_fields.append("classification")

    # ============================================================
    # 🔹 ENROLLMENT TIMESTAMPS (SAFE DEFAULTS)
    # ============================================================
    if instance.enrollment_status == "enrolled" and not instance.enrolled_at:
        now = timezone.now()
        instance.enrolled_at = now
        instance.status_changed_at = now
        update_fields += ["enrolled_at", "status_changed_at"]

    # ============================================================
    # 🔹 SAVE SNAPSHOT (NO RECURSIVE LOOP)
    # ============================================================
    instance.save(update_fields=update_fields)

    # ============================================================
    # 🔹 MANY-TO-MANY (AFTER SAVE)
    # ============================================================
    if profile.designations.exists():
        instance.designations.set(profile.designations.all())

    # ============================================================
    # 🔹 QR CODE (ONE-TIME GENERATION)
    # ============================================================
    if not instance.qr_code:
        instance.generate_qr_code()
        instance.save(update_fields=["qr_code"])


#
# @receiver(post_migrate)
# def create_daily_qr_task(sender, **kwargs):
#     """
#     Automatically create the daily QR regeneration task
#     after migrations are applied.
#     """
#
#     # Avoid running for unrelated apps
#     if sender.name != "student":
#         return
#
#     # Ensure django-celery-beat is installed
#     if not apps.is_installed("django_celery_beat"):
#         return
#
#     CrontabSchedule = apps.get_model("django_celery_beat", "CrontabSchedule")
#     PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
#
#     schedule, _ = CrontabSchedule.objects.get_or_create(
#         minute="0",
#         hour="2",
#     )
#
#     PeriodicTask.objects.get_or_create(
#         name="Daily Student QR Code Maintenance",
#         task="student.tasks.regenerate_student_qr_codes",
#         defaults={
#             "crontab": schedule,
#             "kwargs": json.dumps({"force": False}),
#             "enabled": True,
#         },
#     )
