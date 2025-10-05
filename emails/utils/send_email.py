import os
import django
import sys
import requests

# Set the system path to your Django project

# print("Script Path:", os.path.abspath(__file__))
# Set the settings module
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

# Initialize Django
# django.setup()

import smtplib
import socket
import ssl
from email.mime.text import MIMEText
from django.template.loader import render_to_string
from django.conf import settings

import smtplib
import socket
import ssl
from email.mime.text import MIMEText
from django.template.loader import render_to_string
from django.conf import settings



class EmailSender:
    # Static config from Django settings as defaults
    SMTP_SERVER = settings.EMAIL_HOST
    DEFAULT_PORT = settings.EMAIL_PORT
    DEFAULT_USE_SSL = getattr(settings, 'EMAIL_USE_SSL', False)
    DEFAULT_USE_TLS = getattr(settings, 'EMAIL_USE_TLS', False)
    DOMAIN = getattr(settings, 'CURRENT_DOMAIN', 'localhost')
    TEMPLATE_DIR = 'email/email_templates/'
    DEFAULT_TEMPLATE = 'email_verification.html'

    def __init__(
        self,
        to_email,
        subject,
        template_name=None,
        context=None,
        plain_text=None,
        from_email=None,
        from_email_password=None,
        port=None,
        use_ssl=None,
        use_tls=None,
        host=None,
    ):
        """
        Initialize the email sender with dynamic or default SMTP credentials and options.

        :param to_email: Recipient's email address
        :param subject: Email subject
        :param template_name: Template file name (optional)
        :param context: Context dictionary for rendering template (optional)
        :param plain_text: Optional plain text email content (bypasses template rendering)
        :param from_email: Sender email address (optional; defaults to settings)
        :param from_email_password: Sender email password (optional; defaults to settings)
        :param port: SMTP port (optional; defaults to settings)
        :param use_ssl: Use SSL (optional; defaults to settings)
        :param use_tls: Use TLS (optional; defaults to settings)
        """
        self.to_email = to_email
        self.subject = subject
        self.template_name = template_name or self.DEFAULT_TEMPLATE
        self.context = context or {}
        self.plain_text = plain_text

        self.from_email = from_email or settings.EMAIL_HOST_USER
        self.from_email_password = from_email_password or settings.EMAIL_HOST_PASSWORD
        self.smtp_server = host or self.SMTP_SERVER
        self.port = port or self.DEFAULT_PORT
        self.use_ssl = use_ssl if use_ssl is not None else self.DEFAULT_USE_SSL
        self.use_tls = use_tls if use_tls is not None else self.DEFAULT_USE_TLS

    def send(self):
        print("📨 Preparing to send email...")
        print(f"  - To: {self.to_email}")
        print(f"  - Subject: {self.subject}")
        print(f"  - Template: {self.template_name}")
        print(f"  - From: {self.from_email}")
        print(f"  - Using plain text: {'Yes' if self.plain_text else 'No'}")
        print(f"  - Port: {self.port}")
        print(f"  - Use SSL: {self.use_ssl}")
        print(f"  - Use TLS: {self.use_tls}")

        content_type = 'html'
        html_content = self.plain_text

        if not self.plain_text:
            template_path = f"{self.TEMPLATE_DIR}{self.template_name}"
            try:
                html_content = render_to_string(template_path, self.context)
                print("✅ Template rendered successfully.")
            except Exception as e:
                print("❌ Template rendering failed.")
                return {'success': False, 'message': f'Template rendering error: {e}'}

        msg = MIMEText(html_content, content_type)
        msg['Subject'] = self.subject
        msg['From'] = self.from_email
        msg['To'] = self.to_email

        ssl_context = ssl.create_default_context()

        try:
            if (
                    self.from_email != settings.EMAIL_HOST_USER or
                    self.from_email_password != settings.EMAIL_HOST_PASSWORD
            ):
                print("⚠️ Using dynamic SMTP credentials.")
                print(f"    ⚙️  Respecting provided flags -> use_ssl={self.use_ssl}, use_tls={self.use_tls}")

            if self.use_ssl:
                print(f"🔐 Connecting with SSL on port {self.port}...")
                server = smtplib.SMTP_SSL(self.smtp_server, self.port, context=ssl_context)


            else:
                print(f"📡 Connecting without SSL on port {self.port}...")
                server = smtplib.SMTP(self.smtp_server, self.port)

                server.ehlo()
                if self.use_tls:
                    print("🔐 Upgrading to TLS...")
                    server.starttls(context=ssl_context)
                    server.ehlo()

            print(f"🔑 Logging in as: {self.from_email}")
            server.login(self.from_email, str(self.from_email_password))

            print("📤 Sending email...")
            server.sendmail(self.from_email, [self.to_email], msg.as_string())
            server.quit()

            print("✅ Email sent successfully.")
            return {'success': True, 'message': 'Email sent!'}

        except Exception as e:
            print("❌ SMTP error:", e)
            return {'success': False, 'message': f'SMTP error: {e}'}


# Example Usage (in a Django View)
if __name__=="__main__":
    """
    1. Send with HTML template:
        email_sender.send_email(
            to_email="user@example.com",
            subject="Verify your email",
            url="https://mysite.com/verify",
            app_name="MyCoolApp"
        )
    2. Send with custom template:
        sender = EmailSender(
            to_email="recipient@example.com",
            subject="Reset Your Password",
            template_name="password_reset.html",
            context={"user": "John", "url": "https://reset-link"},
            from_email="noreply@yourdomain.com",
            from_email_password="app_specific_password"
        )
        
        result = sender.send()
             
    3. Send with plain text only (no template):
        email_sender.send_email(
            to_email="user@example.com",
            subject="Simple Text Email",
            plain_text="Hello! This is a simple plain text email without using a template."
        )
    """
    email_sender = EmailSender(
        to_email="eugenereybulahan@gmail.com",
        subject="Reset Password Requested",
        template_name="password_reset_request.html",
        context = {
            'domain': 'cascntp.ph',
            'app_name': 'ONE EMAIL SYSTEM',
            'user': 'Eugene Rey Bulahan',
            'password_reset_url': 'https://cascntp.ph/',
            'team': "Developer's Team"
        }
    )
    email_sender.send()