from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):

    # Columns shown in the list page
    list_display = (
        "student",
        "student_name",
        "date",
        "status",
        "time_in",
        "time_out",
    )

    # Filters on the right side
    list_filter = (
        "status",
        "date",
        "student__user__last_name",
    )

    # Search bar
    search_fields = (
        "student__student_id",
        "student__user__first_name",
        "student__user__last_name",
    )

    # Order results
    ordering = ("-date", "student__user__last_name")

    # Read-only fields (auto-generated)
    readonly_fields = ("time_in", "time_out")

    # Custom field for admin display
    def student_name(self, obj):
        return obj.student.user.get_full_name()
    student_name.short_description = "Full Name"
