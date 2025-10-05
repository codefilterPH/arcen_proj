from rest_framework import viewsets, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from users.models import UserProfile, Organization, Designation, Classification
from django.contrib.auth.models import User
from users.api.serializers import ClassificationSerializer, UserWithProfileSerializer, OrganizationSerializer, DesignationSerializer

from authentication.utils.check_role import CheckUserPermission
from authentication.utils.thread_manager import ThreadManager
from school.utils.pagination import FilterSortPaginate
from django.shortcuts import redirect, get_object_or_404
from users.api.serializers import UserProfileSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes, action
from rest_framework import status
from django.conf import settings
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q


class UserListViewSet(viewsets.ViewSet):
    """
    Returns a paginated list of all users (with UserProfile details).
    Frontend can use Select2 for client-side search.
    """

    @permission_classes([IsAuthenticated])
    def list(self, request):
        try:
            # Pagination params
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 50))
            offset = (page - 1) * page_size

            # Query all users
            users = User.objects.select_related('userprofile').order_by(
                'userprofile__rank', 'first_name', 'last_name'
            )

            total = users.count()
            users = users[offset:offset + page_size]

            data = []
            for user in users:
                profile = getattr(user, 'userprofile', None)
                data.append({
                    "id": user.id,
                    "full_name": str(user.userprofile),
                    "username": user.username,
                    "email": user.email,
                })

            return Response({
                "results": data,
                "page": page,
                "total": total,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ClassificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to view all classifications (for dropdowns).
    """
    queryset = Classification.objects.all().order_by("name")
    serializer_class = ClassificationSerializer
    permission_classes = [permissions.IsAuthenticated]

class DesignationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to view all designations (for dropdowns).
    """
    queryset = Designation.objects.all().order_by("name")
    serializer_class = DesignationSerializer
    permission_classes = [permissions.IsAuthenticated]

class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows organizations to be viewed.
    """
    queryset = Organization.objects.all().order_by('name')
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

class ManageUsers(viewsets.ViewSet):
    # Apply the permission_classes directly to the class
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='get-users')  # Define action and URL pattern
    def get_users(self, request, *args, **kwargs):
        # Check if the user has permission to access this endpoint
        print(f"User {request.user.username} is trying to access the list of users.")

        if not CheckUserPermission.check_role(user=request.user,
                                              group_names=['Developer', 'COUNTPA Manager', 'COUNTPA Supervisor']):
            print("User does not have permission to access this resource.")
            return Response(
                {'detail': 'You do not have permission to access this resource.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            # Fetch all profiles
            profiles = UserProfile.objects.all().select_related('user')
            print(f'PRE PROFILES: {profiles}')  # Print the original queryset

            # If the requester is not a Developer, exclude users with roles in HIDDEN_ROLES
            if not CheckUserPermission.check_role(user=request.user, group_names=['Developer']):
                profiles = profiles.exclude(user__groups__name__in=settings.HIDDEN_ROLES)
                print(f"User is not a Developer. Excluding users with roles in HIDDEN_ROLES: {settings.HIDDEN_ROLES}")
            else:
                print("User is a Developer. Showing all users.")

        except UserProfile.DoesNotExist:
            print("No UserProfile found.")
            return Response(
                {"error": "User profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Serialize the profiles using the UserProfileSerializer
        serializer = UserProfileSerializer(profiles, many=True)
        print(f'SERIALIZED DATA: {serializer.data}')  # Print the serialized data

        # Define the order fields for filtering, sorting, and pagination
        order_fields = [
            'profile_picture',  # Avatar
            'qr_code',
            'fullname',  # Full Name
            'is_active',  # Active Status (coming from auth_user)
            'groups',  # Roles (groups)
            'organization_names',  # Member of
            'last_activity',  # Last Active
        ]

        print(f'ORDER FIELDS: {order_fields}')  # Print the order fields used for sorting and filtering

        # Pass the serialized data to the filter_sort_paginate method
        filtered_data, total_records = FilterSortPaginate().filter_sort_paginate(
            request, serializer.data, order_fields
        )
        print(f'FILTERED DATA: {filtered_data}')  # Print filtered data
        print(f'TOTAL RECORDS: {total_records}')  # Print total records count

        # Response formatting
        response = {
            'draw': int(request.GET.get('draw', 1)),
            'recordsTotal': total_records,
            'recordsFiltered': total_records,
            'data': filtered_data
        }
        print(f'RESPONSE: {response}')  # Print the final response before sending it

        return Response(response, status=status.HTTP_200_OK)

class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet to retrieve and update the authenticated user's profile."""

    permission_classes = [IsAuthenticated]
    serializer_class = UserWithProfileSerializer

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='update-profile')
    def update_info(self, request, *args, **kwargs):
        user_profile = request.user.userprofile
        serializer = UserProfileSerializer(user_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='upload-signature')
    def upload_signature(self, request, *args, **kwargs):
        # Verify the requesting user is authenticated
        user = request.user

        # Get the signature data from the request (Base64 string)
        signature_data = request.data.get('signature')

        if not signature_data:
            return Response({"stop": "No signature data provided"}, status=status.HTTP_200_OK)

        try:
            # Fetch the user's profile (OneToOne relationship)
            user_profile = UserProfile.objects.get(user=user)

            # Save the Base64 string directly to the signature field
            user_profile.signature = signature_data
            user_profile.save()

            return Response({"message": "Signature uploaded successfully"}, status=status.HTTP_200_OK)

        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='upload-profile-picture')
    def upload_profile_picture(self, request, *args, **kwargs):
        user_profile = request.user.userprofile
        profile_picture = request.FILES.get('profile_picture')  # 👈 use FILES, not data.get

        if not profile_picture:
            return Response({"error": "No profile picture provided"}, status=status.HTTP_400_BAD_REQUEST)

        user_profile.profile_picture = profile_picture
        user_profile.save()

        profile_picture_url = request.build_absolute_uri(user_profile.profile_picture.url)

        return Response({
            "message": "Profile picture updated successfully.",
            "profile_picture_url": profile_picture_url
        }, status=status.HTTP_200_OK)