from django.core.management.base import BaseCommand
from django.utils.text import slugify
from schools.models import SchoolOrg


class Command(BaseCommand):
    help = "Fix blank, null, or duplicate slugs for SchoolOrg"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Fixing SchoolOrg slugs..."))

        for school in SchoolOrg.objects.all():
            if not school.slug or school.slug.strip() == "":
                base = slugify(school.name) or "school"
                slug = base
                counter = 1

                # Ensure uniqueness
                while SchoolOrg.objects.filter(slug=slug).exclude(pk=school.pk).exists():
                    slug = f"{base}-{counter}"
                    counter += 1

                school.slug = slug
                school.save(update_fields=["slug"])
                self.stdout.write(self.style.SUCCESS(f"Updated slug for: {school.name} -> {slug}"))

        # Check duplicates after fixing
        from django.db.models import Count
        duplicates = (
            SchoolOrg.objects.values("slug")
            .annotate(c=Count("id"))
            .filter(c__gt=1)
        )

        if duplicates:
            self.stdout.write(self.style.ERROR("Duplicates still exist!"))
            for d in duplicates:
                self.stdout.write(str(d))
        else:
            self.stdout.write(self.style.SUCCESS("All slugs are unique and valid!"))
