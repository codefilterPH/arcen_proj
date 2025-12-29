from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Reset the password and activate/deactivate a given user'

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='?', type=str, help='Username of the user')
        parser.add_argument('password', nargs='?', type=str, help='New password')
        parser.add_argument('--activate', action='store_true', help='Activate the user account')
        parser.add_argument('--deactivate', action='store_true', help='Deactivate the user account')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        activate = options['activate']
        deactivate = options['deactivate']

        if not username:
            # Get username from user input
            username = input("Enter username: ")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f"User '{username}' does not exist")

        if not password:
            # Get new password from user input
            password = input("Enter new password: ")

        # Reset the password
        user.set_password(password)

        if user.is_active and not activate and not deactivate:
            # User is already active, ask if they want to deactivate
            deactivate_input = input("User is already active. Do you want to deactivate? (y/n): ")
            if deactivate_input.lower() == 'y':
                user.is_active = False
        elif not user.is_active and not activate and not deactivate:
            # User is not active, ask if they want to activate
            activate_input = input("User is not active. Do you want to activate? (y/n): ")
            if activate_input.lower() == 'y':
                user.is_active = True

        if activate:
            user.is_active = True
        elif deactivate:
            user.is_active = False

        user.save()

        action = "activated" if activate else "deactivated" if deactivate else "reset"
        self.stdout.write(self.style.SUCCESS(f"Password reset and user '{username}' {action} successfully"))
