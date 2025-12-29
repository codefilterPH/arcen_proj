from rest_framework import serializers
from schools.models import SchoolOrg


# serializers.py
from rest_framework import serializers
from schools.models import SchoolYear

class SchoolYearSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(format="%d %B %Y")
    end_date = serializers.DateField(format="%d %B %Y")

    start_date_raw = serializers.DateField(
        source="start_date", format="%Y-%m-%d", read_only=True
    )
    end_date_raw = serializers.DateField(
        source="end_date", format="%Y-%m-%d", read_only=True
    )

    class Meta:
        model = SchoolYear
        fields = [
            "id",
            "name",
            "start_date",
            "end_date",
            "start_date_raw",
            "end_date_raw",
        ]


class SchoolOrgSerializer(serializers.ModelSerializer):
    """Serializer for SchoolOrg model."""

    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = SchoolOrg
        fields = [
            'id',
            'name',
            'slug',
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
