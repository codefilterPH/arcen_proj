from rest_framework import serializers
from django.contrib.auth.models import User
from student.models import Student
from schools.models import SchoolOrg
from users.models import Designation, Classification

class StudentSerializer(serializers.ModelSerializer):
    """Serializer for Student model (Edit + View compatible)."""

    # -------------------------------------------------
    # 🔹 Computed / Display fields
    # -------------------------------------------------
    full_name = serializers.SerializerMethodField(read_only=True)
    school_name = serializers.CharField(source="school.name", read_only=True)
    profile_image = serializers.SerializerMethodField(read_only=True)
    qr_image = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)

    # -------------------------------------------------
    # 🔹 Relations (for selects)
    # -------------------------------------------------
    designations = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Designation.objects.all(),
        required=False
    )

    classification = serializers.PrimaryKeyRelatedField(
        queryset=Classification.objects.all(),
        allow_null=True,
        required=False
    )

    class Meta:
        model = Student
        fields = [
            # 🔹 Core
            "id",
            "school",
            "school_name",
            "student_id",

            # 🔹 Snapshot Identity (editable but historically stored)
            "rank",
            "first_name",
            "middle_name",
            "last_name",
            "extension_name",
            "email",
            "preferred_initial",
            "display_name_format",

            # 🔹 Personal
            "gender",
            "birth_date",
            "contact_number",

            # 🔹 Academic
            "classification",
            "designations",

            # 🔹 Status / Enrollment
            "enrollment_status",
            "is_active",
            "enrolled_at",
            "status_changed_at",
            "status",

            # 🔹 Visual / Display
            "profile_image",
            "qr_image",
            "full_name",

            # 🔹 Audit
            "joined_date",
            "last_updated",
        ]

        read_only_fields = [
            "student_id",
            "qr_image",
            "joined_date",
            "last_updated",
            "enrolled_at",
            "status_changed_at",
            "full_name",
            "profile_image",
            "school_name",
            "status",
        ]

    # -------------------------------------------------
    # 🔹 Derived fields
    # -------------------------------------------------

    def get_full_name(self, obj):
        return str(obj)

    def get_profile_image(self, obj):
        return obj.get_profile_picture_url()

    def get_qr_image(self, obj):
        if obj.qr_code:
            return f"data:image/png;base64,{obj.qr_code}"
        return None

    def get_status(self, obj):
        if not obj.is_active:
            return "Inactive"

        return {
            "pending": "Pending",
            "enrolled": "Enrolled",
            "on_leave": "On Leave",
            "graduated": "Graduated",
            "transferred": "Transferred",
            "dropped": "Dropped",
        }.get(obj.enrollment_status, "Unknown")