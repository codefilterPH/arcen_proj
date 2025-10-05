from rest_framework import serializers
from django.contrib.auth.models import User
from users.models import UserProfile, Organization, Designation, Classification
from datetime import datetime

class ClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classification
        fields = ["id", "name"]

class DesignationSerializer(serializers.ModelSerializer):
    """Serializer for user designations."""

    class Meta:
        model = Designation
        fields = ["id", "name"]

class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'last_login']

class CustomDateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        if value:
            if value.second == 0:
                return value.strftime("%d %B %Y")
            return value.strftime("%d %B %Y %H:%M")
        return None

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'description']  # keep it light for dropdowns

class UserProfileSerializer(serializers.ModelSerializer):
    user = AuthUserSerializer(required=False)
    classification = ClassificationSerializer(read_only=True)
    classification_id = serializers.PrimaryKeyRelatedField(
        queryset=Classification.objects.all(),
        source="classification",
        write_only=True,
        required=False,
        allow_null=True
    )

    designations = DesignationSerializer(many=True, read_only=True)
    designation_ids = serializers.PrimaryKeyRelatedField(
        queryset=Designation.objects.all(),
        many=True,
        source="designations",
        write_only=True,
        required=False
    )

    organizations = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    default_organization_id = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        source="default_organization",
        write_only=True,
        required=False,
        allow_null=True
    )
    default_organization_name = serializers.SerializerMethodField(read_only=True)

    organization_names = serializers.SerializerMethodField(read_only=True)
    organization_ids = serializers.SerializerMethodField(read_only=True)
    profile_picture = serializers.SerializerMethodField(read_only=True)
    groups = serializers.SerializerMethodField(read_only=True)
    fullname = serializers.SerializerMethodField(read_only=True)
    is_active = serializers.SerializerMethodField(read_only=True)

    last_activity = CustomDateTimeField(read_only=True)
    last_password_reset = CustomDateTimeField(read_only=True)
    qr_code = serializers.SerializerMethodField(read_only=True)   # 👈 expose QR as base64

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user',
            'rank', 'sub_svc', 'middle_name', 'preferred_initial', 'extension_name',
            'gender', 'birth_date', 'bio', 'profile_picture', 'default_avatar',
            'signature', 'position',
            'classification', 'classification_id',
            'designations', 'designation_ids',
            'organizations',
            'default_organization_id', 'default_organization_name',
            'organization_ids', 'organization_names',
            'email_verified', 'contact_number', 'last_activity', 'last_password_reset',
            'fullname', 'groups', 'is_active', 'display_name_format', 'qr_code'
        ]

    def update(self, instance, validated_data):
        # Handle nested user update
        user_data = validated_data.pop('user', None)
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        # Handle organizations
        orgs = validated_data.pop("organizations", None)
        if orgs is not None:
            instance.organizations.set(orgs)

            if instance.default_organization and instance.default_organization not in orgs:
                instance.default_organization = None

        # Handle default_organization separately
        default_org = validated_data.pop("default_organization", None)
        if default_org:
            if instance.organizations.filter(id=default_org.id).exists():
                instance.default_organization = default_org
            else:
                raise serializers.ValidationError({
                    "default_organization": [
                        "The default organization must be one of the assigned organizations."
                    ]
                })

        return super().update(instance, validated_data)

    def get_default_organization_name(self, obj):
        return obj.default_organization.name if obj.default_organization else None

    def get_organization_names(self, obj):
        return [org.name for org in obj.organizations.all()]

    def get_organization_ids(self, obj):
        return [org.id for org in obj.organizations.all()]

    def get_profile_picture(self, obj):
        return obj.get_profile_picture_url

    def get_fullname(self, obj):
        return str(obj)

    def get_groups(self, obj):
        return [group.name for group in obj.user.groups.all()]

    def get_is_active(self, obj):
        return obj.user.is_active

    def get_qr_code(self, obj):
        """Return QR code as a base64 data URI usable in <img src="">."""
        if obj.qr_code:
            return f"data:image/png;base64,{obj.qr_code}"
        return None


class UserWithProfileSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source='userprofile', read_only=True)
    groups = serializers.SerializerMethodField()
    is_authenticated = serializers.SerializerMethodField()

    def get_groups(self, obj):
        return [group.name for group in obj.groups.all()]

    def get_is_authenticated(self, obj):
        return obj.is_authenticated

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'groups', 'profile', 'is_authenticated']
