
from django.contrib import admin
from .models import Student, FlightMembership


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_id", "full_name", "school", "joined_date")
    list_filter = ("school", "joined_date")
    search_fields = (
        "student_id",
        "user__username",
        "user__first_name",
        "user__last_name",
        "school__name",
    )
    ordering = ("student_id",)

    def full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    full_name.short_description = "Student Name"


@admin.register(FlightMembership)
class FlightMembershipAdmin(admin.ModelAdmin):
    list_display = ("student_display", "flight_display", "joined_at")
    list_filter = ("flight__class_obj__semester__school_year__school", "flight", "joined_at")
    search_fields = (
        "student__student_id",
        "student__user__first_name",
        "student__user__last_name",
        "flight__name",
        "flight__class_obj__name",
    )
    ordering = ("-joined_at",)

    def student_display(self, obj):
        return f"{obj.student.user.get_full_name()} ({obj.student.student_id})"
    student_display.short_description = "Student"

    def flight_display(self, obj):
        return str(obj.flight)
    flight_display.short_description = "Flight"

