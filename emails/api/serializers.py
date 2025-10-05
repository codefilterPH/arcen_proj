# emails/serializers.py
from rest_framework import serializers


class EmailRequestSerializer(serializers.Serializer):
    to_email = serializers.EmailField()
    from_email = serializers.EmailField()
    from_email_password = serializers.CharField(write_only=True)
    subject = serializers.CharField()
    smtp_server = serializers.CharField()
    template_name = serializers.CharField(required=False, allow_blank=True)
    context = serializers.DictField(required=False)  # Accepts any dict
    port = serializers.IntegerField(required=False)
    use_ssl = serializers.BooleanField(required=False)
    use_tls = serializers.BooleanField(required=False)
