from django.contrib import admin
from .models import SchoolOrg, SchoolYear, Semester, Class, Flight


@admin.register(SchoolOrg)
class SchoolOrgAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "logo_preview", "created_at", "updated_at")
    search_fields = ("name", "address")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at", "logo_preview")

    fieldsets = (
        (None, {
            "fields": ("name", "address", "logo", "logo_preview")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
        }),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return f'<img src="{obj.logo.url}" style="max-height: 60px; max-width: 60px; border-radius:4px;" />'
        return "No Logo"
    logo_preview.allow_tags = True
    logo_preview.short_description = "Logo Preview"



# 🔹 Inline Models
class SemesterInline(admin.TabularInline):
    model = Semester
    extra = 1


class SchoolYearInline(admin.TabularInline):
    model = SchoolYear
    extra = 1


class ClassInline(admin.TabularInline):
    model = Class
    extra = 1


class FlightInline(admin.TabularInline):
    model = Flight
    extra = 1


# 🔹 SchoolYear Admin
@admin.register(SchoolYear)
class SchoolYearAdmin(admin.ModelAdmin):
    list_display = ("name", "school", "start_date", "end_date")
    list_filter = ("school", "start_date")
    search_fields = ("name", "school__name")
    ordering = ("-start_date",)
    inlines = [SemesterInline]


# 🔹 Semester Admin
@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ("name", "school_year", "start_date", "end_date")
    list_filter = ("school_year__school", "school_year", "start_date")
    search_fields = ("name", "school_year__name", "school_year__school__name")
    ordering = ("-start_date",)
    inlines = [ClassInline]


# 🔹 Class Admin
@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "semester", "instructor_display")
    list_filter = ("semester__school_year__school", "semester__name")
    search_fields = ("code", "name", "instructor__username", "semester__name")
    ordering = ("code",)
    inlines = [FlightInline]

    def instructor_display(self, obj):
        return obj.instructor.get_full_name() if obj.instructor else "—"
    instructor_display.short_description = "Instructor"


# 🔹 Flight Admin
@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ("name", "class_obj_display")
    list_filter = ("class_obj__semester__school_year__school", "class_obj__semester")
    search_fields = ("name", "class_obj__code", "class_obj__name")
    ordering = ("name",)

    def class_obj_display(self, obj):
        return f"{obj.class_obj.code} - {obj.class_obj.name}"
    class_obj_display.short_description = "Class"
