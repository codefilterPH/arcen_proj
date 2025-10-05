# emails/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from emails.api.serializers import EmailRequestSerializer
from emails.utils.send_email import EmailSender
from authentication.permissions.permissions import JWTOrApiKeyPermission


class EmailSenderViewSet(viewsets.ViewSet):
    permission_classes = [JWTOrApiKeyPermission]

    @action(detail=False, methods=['post'], url_path='send')
    def send_email(self, request):
        """
        Send a custom email with dynamic context and template.
        """
        serializer = EmailRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            print(f'API DATA RECEIVED: {data}')

            email_sender = EmailSender(
                to_email=data['to_email'],
                subject=data['subject'],
                template_name=data.get('template_name'),  # safer to use get()
                context=data.get('context', {}),
                from_email=data.get('from_email'),
                from_email_password=data.get('from_email_password'),
                host=data.get('smtp_server'),
                port=data.get('port'),
                use_ssl=data.get('use_ssl'),
                use_tls=data.get('use_tls'),
            )

            result = email_sender.send()
            return Response(result,
                            status=status.HTTP_200_OK if result['success'] else status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
