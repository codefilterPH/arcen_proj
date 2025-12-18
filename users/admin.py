from django.contrib import admin
from .models import UserProfile, Designation, Organization, Classification
from users.forms import UserProfileAdminForm
from django.utils.html import format_html


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    form = UserProfileAdminForm  # your custom form

    list_display = (
        "user", "rank", "sub_svc", "position", "classification",
        "email_verified", "last_activity"
    )

    list_filter = (
        "email_verified", "gender", "classification",
        "last_activity", "designations"
    )

    search_fields = (
        "user__username", "user__first_name", "user__last_name",
        "contact_number", "rank", "sub_svc", "position"
    )

    autocomplete_fields = (
        "user", "classification", "designations", "organizations", "default_organization"
    )

    filter_horizontal = ("organizations", "designations")

    readonly_fields = ("qr_code_preview",)

    fieldsets = (
        ("User Information", {
            "fields": (
                "user", "rank", "sub_svc", "middle_name",
                "preferred_initial", "extension_name", "gender", "birth_date"
            )
        }),

        ("Contact Information", {
            "fields": (
                "contact_number", "email_verified",
                "last_activity", "last_password_reset"
            )
        }),

        ("Address Information", {
            "fields": (
                "address", "city", "province",
            )
        }),

        ("Organization Details", {
            "fields": (
                "organizations", "default_organization",
                "position", "classification", "designations", "course"
            )
        }),

        ("Profile & Display", {
            "fields": (
                "bio", "profile_picture", "default_avatar",
                "signature", "display_name_format"
            )
        }),

        ("QR Code", {
            "fields": ("qr_code_preview", "qr_code")
        }),
    )

    # -------------------------------------------
    # QR Code Preview (show image instead of Base64)
    # -------------------------------------------
    def qr_code_preview(self, obj):
        if not obj.qr_code:
            return "No QR Code"
        return format_html(
            '<img src="data:image/png;base64,{}" style="width:200px;border:1px solid #ccc;padding:5px;border-radius:8px;" />',
            obj.qr_code
        )

    qr_code_preview.short_description = "QR Code Preview"

    # -------------------------------------------
    # Admin Action: Regenerate QR for selected users
    # -------------------------------------------
    actions = ["regenerate_qr"]

    def regenerate_qr(self, request, queryset):
        count = 0
        for profile in queryset:
            profile.generate_qr_code(force=True)
            profile.save(update_fields=["qr_code"])
            count += 1

        self.message_user(request, f"QR Code regenerated for {count} user(s).")

    regenerate_qr.short_description = "Regenerate QR Code for selected users"

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
