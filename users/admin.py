from django.contrib import admin
from .models import UserProfile, Designation, Organization, Classification
from users.forms import UserProfileAdminForm

@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    form = UserProfileAdminForm  # 👈 assign the custom form

    list_display = (
        "user", "rank", "sub_svc", "position", "classification",
        "default_organization", "email_verified", "last_activity"
    )
    list_filter = (
        "email_verified", "gender", "last_activity",
        "classification", "organizations"
    )
    search_fields = (
        "user__username", "user__first_name", "user__last_name",
        "contact_number", "rank", "sub_svc", "position"
    )
    autocomplete_fields = ("user", "organizations", "default_organization", "classification", "designations")
    filter_horizontal = ("organizations", "designations")

    fieldsets = (
        ("User Information", {
            "fields": (
                "user", "rank", "sub_svc", "middle_name",
                "preferred_initial", "extension_name", "gender", "birth_date"
            )
        }),
        ("Contact & Status", {
            "fields": (
                "contact_number", "email_verified",
                "last_activity", "last_password_reset"
            )
        }),
        ("Organization Details", {
            "fields": (
                "organizations", "default_organization",
                "position", "classification", "designations"
            )
        }),
        ("Profile & Security", {
            "fields": (
                "bio", "profile_picture", "default_avatar",
                "signature", "display_name_format", "qr_code"
            )
        }),
    )


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_person", "contact_number", "email", "owner", "created_at")
    search_fields = ("name", "contact_person", "email")
    list_filter = ("created_at",)
    autocomplete_fields = ("owner",)


@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)
