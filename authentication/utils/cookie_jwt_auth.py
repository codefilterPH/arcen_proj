from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom authentication to read JWT tokens from HttpOnly cookies.
    """

    def authenticate(self, request):
        # Try to get token from cookie instead of header
        access_token = request.COOKIES.get("access")

        if access_token:
            validated_token = self.get_validated_token(access_token)
            return self.get_user(validated_token), validated_token

        return None
