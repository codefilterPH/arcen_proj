from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.apps import apps
from .models import UserProfile
from django.contrib.auth.models import Group

GROUPS = [
    'DEVELOPER', 'ADMINISTRATOR', 'CIES',
    'MTI', 'STUDENTS'
]

@receiver(post_migrate)
def create_groups(sender, **kwargs):
    """Signal handler for post_migrate to create predefined user groups."""
    for group_name in GROUPS:
        Group.objects.get_or_create(name=group_name)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a UserProfile when a new User is created."""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_migrate)
def create_profiles_for_existing_users(sender, **kwargs):
    """Ensure all existing users have a UserProfile after migration."""
    if sender.name == 'users':  # Run only when the 'users' app is migrated
        User = apps.get_model('auth', 'User')
        for user in User.objects.all():
            UserProfile.objects.get_or_create(user=user)
