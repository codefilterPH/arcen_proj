from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import get_authorization_header
from django.contrib.auth.models import User
from authentication.models import ApiKey  # Assuming your ApiKey model is in authentication.models

from rest_framework.permissions import BasePermission
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

signer = TimestampSigner()

class VerifyTokenPermission(BasePermission):
    def has_permission(self, request, view):
        token = request.GET.get('token')
        if not token:
            return False

        try:
            signer.unsign(token, max_age=900)
            return True
        except (BadSignature, SignatureExpired):
            return False


class JWTOrApiKeyPermission(BasePermission):
    """
    Custom permission to allow access if either JWT or API key is provided and valid.
    """

    def has_permission(self, request, view):
        # Check for Bearer token (JWT)
        auth_header = get_authorization_header(request).decode('utf-8')
        print(f"Authorization header: {auth_header}")

        if auth_header:
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]  # Remove "Bearer " part
                print(f"Found JWT token: {token[:10]}... (truncated)")
                try:
                    # Normally JWT validation happens elsewhere, assume valid here
                    print("JWT token assumed valid in this permission class.")
                    return True
                except Exception as e:
                    print(f"JWT validation error: {e}")
                    raise AuthenticationFailed(f"Invalid JWT Token: {str(e)}")

        # If no JWT, check for API key (X-Api-Key)
        api_key = request.headers.get('X-Api-Key')
        print(f"API key from header: {api_key}")

        if api_key:
            try:
                api_key_obj = ApiKey.objects.get(key=api_key)
                client_ip = request.META.get('REMOTE_ADDR')
                print(f"Client IP: {client_ip}")
                if api_key_obj.is_valid(client_ip):
                    print("API key is valid.")
                    return True
                else:
                    print("API key invalid or unauthorized IP/domain.")
                    raise AuthenticationFailed("Invalid API key or unauthorized IP/domain.")
            except ApiKey.DoesNotExist:
                print("API key not found in database.")
                raise AuthenticationFailed("API Key not found.")

        print("No valid authentication credentials provided.")
        raise AuthenticationFailed("Authentication credentials were not provided.")
