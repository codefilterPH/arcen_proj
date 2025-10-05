from rest_framework import serializers
from schools.models import SchoolOrg

class SchoolOrgSerializer(serializers.ModelSerializer):
    """Serializer for SchoolOrg model."""

    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = SchoolOrg
        fields = [
            'id',
            'name',
            'address',
            'logo',       # for upload
            'logo_url',   # for display (absolute URL)
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_logo_url(self, obj):
        """Return absolute URL of logo if uploaded."""
        request = self.context.get("request")
        if obj.logo and hasattr(obj.logo, "url"):
            return request.build_absolute_uri(obj.logo.url) if request else obj.logo.url
        return None
