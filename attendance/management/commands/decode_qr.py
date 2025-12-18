import base64
import io
import json
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from PIL import Image
from pyzbar.pyzbar import decode as qr_decode
from users.models import UserProfile


class Command(BaseCommand):
    help = "Decode the QR code stored in a user's UserProfile."

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="Username to decode QR")

    def handle(self, *args, **options):
        username = options["username"]

        # Get User
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f"User '{username}' does not exist.")

        # Get Profile
        try:
            profile = user.userprofile
        except UserProfile.DoesNotExist:
            raise CommandError(f"User '{username}' has no UserProfile.")

        if not profile.qr_code:
            raise CommandError(f"User '{username}' has no stored QR code.")

        self.stdout.write(self.style.SUCCESS(f"Decoding QR for user: {username}"))

        try:
            # Decode Base64 → PNG
            qr_bytes = base64.b64decode(profile.qr_code)
            image = Image.open(io.BytesIO(qr_bytes))

            # Decode QR content
            decoded_list = qr_decode(image)
            if not decoded_list:
                raise CommandError("No QR data found in the image.")

            decoded_text = decoded_list[0].data.decode("utf-8")

            # Try converting JSON
            try:
                qr_json = json.loads(decoded_text)
                formatted_json = json.dumps(qr_json, indent=4)
                self.stdout.write(self.style.SUCCESS("QR Data Decoded:"))
                self.stdout.write(formatted_json)

            except json.JSONDecodeError:
                self.stdout.write(self.style.WARNING("QR contains non-JSON text:"))
                self.stdout.write(decoded_text)

        except Exception as e:
            raise CommandError(f"Failed to decode QR: {e}")
