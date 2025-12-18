from rest_framework import serializers
from django.contrib.auth.models import User
from student.models import Student
from schools.models import SchoolOrg


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for Student model."""
    # 🔹 Computed / formatted fields
    full_name = serializers.SerializerMethodField(read_only=True)
    school_name = serializers.CharField(source='school.name', read_only=True)
    profile_image = serializers.SerializerMethodField(read_only=True)
    qr_image = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Student
        fields = [
            'id',
            'school',
            'school_name',
            'student_id',
            'full_name',
            'gender',
            'profile_image',
            'qr_image',
            'status',
            'birth_date',
            'contact_number',
            'joined_date',
            'last_updated',
        ]
        read_only_fields = [
            'student_id', 'qr_image', 'joined_date', 'last_updated'
        ]

    # ------------------------------------------------------------------
    # 🔹 Derived / formatted field getters
    # ------------------------------------------------------------------
    def get_full_name(self, obj):
        """Use Student.__str__() for consistent display format."""
        return str(obj)

    def get_profile_image(self, obj):
        """Returns profile picture URL or default avatar."""
        return obj.get_profile_picture_url()

    def get_qr_image(self, obj):
        """Return Base64 QR code as data URL (for <img src="...">)."""
        if obj.qr_code:
            return f"data:image/png;base64,{obj.qr_code}"
        return None

    def get_status(self, obj):
        """Return static 'Enrolled' status for now (can be dynamic later)."""
        return "Enrolled"
