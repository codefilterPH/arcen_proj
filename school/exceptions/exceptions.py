# exceptions.py

from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from django.utils.encoding import force_str

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Initialize an empty list to collect error messages
        error_messages = []

        # Handle ValidationError separately to extract detailed messages
        if isinstance(exc, ValidationError):
            for field, messages in exc.detail.items():
                if isinstance(messages, list):
                    error_messages.extend([force_str(msg) for msg in messages])
                else:
                    error_messages.append(force_str(messages))
        else:
            # For other exceptions, use the default detail message
            error_messages.append(force_str(exc.detail))

        # Join all error messages into a single string
        error_message = " ".join(error_messages)

        # Set the response data to the unified error format
        response.data = {'error': error_message}

    return response
