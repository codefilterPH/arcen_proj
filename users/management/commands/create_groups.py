from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Create default user roles/groups for the document system'

    def handle(self, *args, **kwargs):
        groups = [
            ("Administrator", "CRUD Documents (No Approval) and Configurations"),
            ("Secretary", "CRUD Documents (Approve and Submit for Publication)"),
            ("Employee", "CRUD Documents (No Approval)"),
            ("Drafter", "Can initiate and edit drafts before approval"),
            ("President", "CRUD Documents (Approve/Disapprove/Comment)"),
            ("Vice President", "CRUD Documents (Approve/Disapprove/Comment)"),
            ("Manager", "CRUD Documents (Approve/Disapprove/Comment)"),
            ("Secretariat", "CRUD Documents, Publish, Upload to Library"),
            ("ExA", "CRUD Documents, Publish, Upload to Library"),
            ("Developer", "System Creator"),
            ("Committee Member", "CRUD Documents, View/Approve Board and Committee Files"),
            ("Satellite Manager", "Manages Satellite Branch Documents and Approvals"),
            ("Human Resource", "Human Resources — Reviews, Approves, and Manages Employee Documents"),
            ("EVP for Operations", "Executive VP for Operations — Oversees and Approves Operational Documents"),
            ("Board of Director", "CRUD Documents, View/Approve Board and Committee Files"),
            ("Chairperson", "Leads the board, approves strategic and policy documents"),  # 👈 NEW
            ("Vice Chairperson", "Assists Chairperson, signs and reviews key documents"),  # 👈 NEW
        ]

        for group_name, description in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Created group: {group_name}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ Group already exists: {group_name}"))
