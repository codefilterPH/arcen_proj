
from users.models import UserProfile
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from authentication.api.serializers import UserLoginSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib import messages

# API MANAGE
from authentication.models import ApiKey
from authentication.api.serializers import ApiKeySerializer
from rest_framework.permissions import IsAuthenticated
from authentication.utils.check_role import CheckUserPermission
from school.utils.date_formatter import DateTimeConverter
from school.utils.pagination import FilterSortPaginate
from rest_framework.exceptions import ValidationError
from django.core.validators import validate_ipv4_address

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature

from authentication.permissions.permissions import VerifyTokenPermission
from emails.utils.send_email import EmailSender

signer = TimestampSigner()
TOKEN_EXPIRY_SECONDS = 900  # 15 minutes

class PasswordResetViewSet(viewsets.ViewSet):
    """
    Handles password reset flow:
    - request token via username & email
    - validate token and redirect to reset page
    - set new password
    """
    authentication_classes = []  # ⛔️ No token authentication by default
    permission_classes = [AllowAny]  # ✅ Allow all unauthenticated users

    @action(detail=False, methods=['post'], url_path='request')
    def password_reset_request(self, request):
        username = request.data.get('username')
        email = request.data.get('email')

        print(f"🔐 Password reset request received.")
        print(f"🧑 Username: {username}")
        print(f"📧 Email: {email}")

        try:
            user = User.objects.get(username=username, email=email)
            print(f"✅ User found: {user.username} (ID: {user.id})")
        except User.DoesNotExist:
            print(f"❌ No user found matching username '{username}' and email '{email}'")
            return Response({'error': 'Invalid username or email'}, status=status.HTTP_404_NOT_FOUND)

        token = signer.sign(user.pk)
        print(f"🔑 Token generated: {token}")

        reset_url = f"{settings.CURRENT_DOMAIN}/api/password-reset/verify-token/?token={token}"
        print(f"🔗 Password reset link: {reset_url}")

        # Define the expiration duration (e.g. 15 minutes)
        expiration_duration = timedelta(minutes=15)
        expiration_time = timezone.now() + expiration_duration
        formatted_expiration = expiration_time.strftime('%I:%M %p %Z')

        email_sender = EmailSender(
            to_email=user.email,
            subject="Reset Password Requested",
            template_name="password_reset_request.html",
            context={
                "domain": "countpaledger.ph",
                "app_name": "ONE EMAIL SYSTEM",
                # "domain": "localhost:8009",
                "user": f"{user.userprofile}",
                "url": f"{reset_url}",
                "team": "Developer's Team",
                "link_expiration_time": f"in 15 minutes (by {formatted_expiration})",
            }
        )

        email_sender.send()
        print(f"📨 Email sent to {user.email}")

        return Response({'message': 'Password reset email sent.'})

    @action(detail=False, methods=['get'], url_path='verify-token', permission_classes=[VerifyTokenPermission])
    def verify_reset_token(self, request):
        token = request.GET.get('token')
        try:
            user_id = signer.unsign(token, max_age=TOKEN_EXPIRY_SECONDS)
            reset_url = reverse('authentication:reset_password_view') + f'?uid={user_id}&token={token}'
            return redirect(reset_url)
        except SignatureExpired:
            return redirect(reverse('authentication:page_403_view'))
        except BadSignature:
            return redirect(reverse('authentication:page_403_view'))

    @action(detail=False, methods=['post'], url_path='reset')
    def reset_password(self, request):
        user_id = request.data.get('uid')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not all([user_id, new_password, confirm_password]):
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk=user_id)
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password successfully reset.'})
        except User.DoesNotExist:
            return Response({'error': 'Invalid user.'}, status=status.HTTP_404_NOT_FOUND)

class ApiKeyViewSet(viewsets.ModelViewSet):
    queryset = ApiKey.objects.all().order_by('-created_at')
    serializer_class = ApiKeySerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='api-keys-list')
    def api_list(self, request, *args, **kwargs):
        # Check if the user has the required role (e.g., 'Developers')
        if not CheckUserPermission.check_role(request.user, group_names=['Developers']):
            return Response({"detail": "You do not have permission to view this."}, status=status.HTTP_403_FORBIDDEN)

        # Get the 'is_active' parameter from the query string
        is_active = request.query_params.get('is_active', None)
        print(f'IS ACTIVE? {is_active}')

        # Start with the base queryset
        filtered_queryset = self.queryset

        # Filter by 'is_active' if provided
        if is_active is not None:
            try:
                is_active_bool = is_active.lower() == 'true'  # Convert string to boolean
                filtered_queryset = filtered_queryset.filter(is_active=is_active_bool)
            except ValueError:
                raise ValidationError({"detail": "Invalid is_active format. Must be 'true' or 'false'."})

        # Serialize the filtered records
        serialized_records = self.serializer_class(filtered_queryset, many=True).data
        print(f'API KEY SERIALIZED RECORDS: {serialized_records}')
        date_formatter = DateTimeConverter()
        # Add an empty "actions" field to each record
        for record in serialized_records:
            # Ensure that 'end_time' exists, then format it to 'expires_at'
            if 'expires_at' in record:
                record['expires_at'] = date_formatter.military_format(record['expires_at'])
            else:
                record['expires_at'] = "N/A"  # Handle case where 'end_time' doesn't exist

            record['actions'] = "No actions atm..."  # Add an empty actions field

        # Define the fields that can be ordered
        order_fields = ['name', 'key', 'is_active', 'expires_at', 'allowed_ip_address', 'allowed_domain', 'actions']

        # Use the custom FilterSortPaginate class for sorting and pagination
        filtered_data, total_records = FilterSortPaginate.filter_sort_paginate(
            request=request,
            records=serialized_records,
            order_fields=order_fields
        )

        # Build the response
        response_data = {
            'draw': int(request.GET.get('draw', 1)),  # Ensure 'draw' is an integer
            'recordsTotal': total_records,
            'recordsFiltered': total_records,
            'data': filtered_data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='api-keys-generate')
    def api_create(self, request, *args, **kwargs):
        """
        Handle the creation of a new API Key.
        """
        # Check if the user has the required role (e.g., 'Developers')
        if not CheckUserPermission.check_role(request.user, group_names=['Developers']):
            return Response({"detail": "You do not have permission to view this."}, status=status.HTTP_403_FORBIDDEN)

        # Log the received data for debugging
        print("Received data:", request.data)  # Print or log the incoming data

        # Extract allowed IP address and domain from the request
        allowed_ip_address = request.data.get('allowed_ip_address')
        allowed_domain = request.data.get('allowed_domain')

        # Validate allowed IP address if provided
        if allowed_ip_address:
            try:
                validate_ipv4_address(allowed_ip_address)
            except ValidationError:
                return Response({"detail": f"'{allowed_ip_address}' is not a valid IPv4 address."},
                                status=status.HTTP_400_BAD_REQUEST)

        # Optionally validate allowed domain if needed (e.g., basic format check)
        if allowed_domain:
            if len(allowed_domain) > 255:  # Just a basic check for domain length
                return Response({"detail": "Domain exceeds maximum length of 255 characters."},
                                status=status.HTTP_400_BAD_REQUEST)

        # Deserialize the data from the request body
        serializer = self.get_serializer(data=request.data)

        # Validate and save the new API Key
        if serializer.is_valid():
            api_key = serializer.save()  # Save the new API Key object

            # Return a success response with the serialized data
            return Response(
                self.get_serializer(api_key).data,
                status=status.HTTP_201_CREATED
            )
        else:
            # Return a failure response if the data is invalid
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['delete'], url_path='api-keys-delete')
    def api_delete(self, request, *args, **kwargs):
        """
        Handle the deletion of an API Key.
        """
        # Check if the user has the required role (e.g., 'Developers')
        if not CheckUserPermission.check_role(request.user, group_names=['Developers']):
            return Response({"detail": "You do not have permission to delete this."}, status=status.HTTP_403_FORBIDDEN)

        # Retrieve the API key object using the provided ID
        try:
            api_key = self.get_object()  # This assumes the ID is passed in the URL
        except ApiKey.DoesNotExist:
            return Response({"detail": "API key not found."}, status=status.HTTP_404_NOT_FOUND)

        # Delete the API key
        api_key.delete()

        # Return a success response
        return Response({"message": "API key deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class UserLoginViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    @action(detail=False, methods=['post'], url_path="login")
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        if not user or not user.is_active:
            return Response({"error": "Invalid credentials or inactive user"}, status=401)

        login(request, user)
        refresh = RefreshToken.for_user(user)

        response = Response({"message": "Login successful"}, status=200)
        # ✅ HttpOnly secure cookies
        response.set_cookie(
            key="access",
            value=str(refresh.access_token),
            httponly=True,
            secure=True,
            samesite="Strict",
            max_age=300  # 5 minutes
        )
        response.set_cookie(
            key="refresh",
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite="Strict",
            max_age=7 * 24 * 60 * 60  # 1 week
        )
        return response

    @action(detail=False, methods=['post'], url_path="logout")
    def logout(self, request):
        try:
            print("🚪 LOGOUT INITIATED")

            # Get the refresh token from the cookie
            refresh_token = request.COOKIES.get("refresh")

            if not refresh_token:
                return Response({'error': 'No refresh token cookie found'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Blacklist the token
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                # If already invalid/expired → still proceed with cookie clearing
                pass

            # Clear cookies
            response = Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
            response.delete_cookie("access")
            response.delete_cookie("refresh")

            # Clear Django session (if using)
            request.session.flush()
            logout(request)

            return response

        except Exception as e:
            return Response({'error': f'Unexpected error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path="refresh")
    def refresh(self, request):
        refresh_token = request.COOKIES.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token missing"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            new_access = refresh.access_token
            response = Response({"message": "Access token refreshed"}, status=200)

            # overwrite cookie
            response.set_cookie(
                key="access",
                value=str(new_access),
                httponly=True,
                secure=True,
                samesite="Strict",
                max_age=300  # 5 minutes
            )
            return response

        except Exception as e:
            return Response({"error": "Invalid or expired refresh token"}, status=status.HTTP_401_UNAUTHORIZED)