from rest_framework import serializers
from authentication.models import ApiKey
from rest_framework.fields import IPAddressField


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    remember_me = serializers.BooleanField(required=False, default=False)

class ApiKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiKey
        fields = ['id', 'name', 'key', 'is_active', 'expires_at', 'allowed_ip_address', 'allowed_domain']

    # Allow null or empty values for allowed_ip_address and allowed_domain
    allowed_ip_address = IPAddressField(required=False, allow_blank=True, allow_null=True)
    allowed_domain = serializers.CharField(required=False, allow_blank=True, allow_null=True)