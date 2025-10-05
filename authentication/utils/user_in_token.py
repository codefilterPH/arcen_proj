import argparse
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
import django
import os

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()


def decode_token(token_str):
    try:
        # Decode token
        token = AccessToken(token_str)
        user_id = token.payload.get("user_id")
        print(f"Decoded Token: {token.payload}")

        # Retrieve user from database
        User = get_user_model()
        user = User.objects.get(id=user_id)
        print(f"User: {user.username} (ID: {user.id})")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Decode JWT token and retrieve user.")
    parser.add_argument("token", type=str, help="JWT access token")
    args = parser.parse_args()

    decode_token(args.token)
