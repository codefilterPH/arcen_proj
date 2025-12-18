from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Create dummy users for each group and update first_name, last_name, and position only for them'

    def handle(self, *args, **kwargs):
        groups = Group.objects.all()
        created_count = 0
        updated_count = 0
        skipped_count = 0

        for group in groups:
            for i in range(1, 6):  # Limit to dummy pattern
                username = f"{group.name.lower().replace(' ', '_')}_{i}"
                email = f"{username}@example.com"

                if User.objects.filter(username=username).exists():
                    user = User.objects.get(username=username)
                    user.groups.add(group)  # Ensure group is added

                    profile, _ = UserProfile.objects.get_or_create(user=user)
                    first_group = user.groups.first()
                    position = first_group.name if first_group else "Unknown"
                    profile.position = position
                    profile.save()

                    # Update first_name and last_name safely for dummy users
                    user.first_name = position.split()[0].capitalize()
                    user.last_name = (
                        position.split()[-1].capitalize()
                        if len(position.split()) > 1 else "Member"
                    )
                    user.save()

                    self.stdout.write(self.style.WARNING(
                        f"🔁 Updated dummy user: {username} with position '{position}', name: {user.first_name} {user.last_name}"
                    ))
                    updated_count += 1
                    continue

                # Create new dummy user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=None  # No password set
                )
                user.groups.add(group)

                position = group.name
                user.first_name = position.split()[0].capitalize()
                user.last_name = (
                    position.split()[-1].capitalize()
                    if len(position.split()) > 1 else "Member"
                )
                user.save()

                UserProfile.objects.create(
                    user=user,
                    position=position
                )

                self.stdout.write(self.style.SUCCESS(
                    f"✅ Created dummy user: {username} → {user.first_name} {user.last_name} | Position: {position}"
                ))
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"\n🎉 Done! Created: {created_count}, Updated: {updated_count}, Skipped: {skipped_count}"
        ))
