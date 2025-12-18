# students/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Student
from users.models import UserProfile  # adjust import if your profile app differs

@receiver(post_save, sender=Student)
def sync_userprofile_to_student(sender, instance, created, **kwargs):
    """
    When a Student is created, copy key data from the linked UserProfile.
    """
    if not created:
        return

    user = instance.user
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        print(f"[WARN] No UserProfile found for user {user}")
        return

    # Copy base info
    instance.gender = profile.gender
    instance.birth_date = profile.birth_date
    instance.contact_number = profile.contact_number
    instance.email_verified = profile.email_verified

    # Copy visual info
    if profile.profile_picture:
        instance.profile_picture = profile.profile_picture
    if profile.default_avatar:
        instance.default_avatar = profile.default_avatar
    instance.display_name_format = profile.display_name_format

    # Copy academic/org info
    instance.classification = profile.classification

    # Save first to ensure we can M2M add
    instance.save()

    # Copy designations (many-to-many)
    if profile.designations.exists():
        instance.designations.set(profile.designations.all())

    # Generate QR code if not yet done
    if not instance.qr_code:
        instance.generate_qr_code()
        instance.save(update_fields=["qr_code"])

    print(f"✅ Synced UserProfile → Student ({user.username})")
