from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connection, models
from django.utils.text import slugify


class Command(BaseCommand):
    help = "Check for missing tables or fields in models and create them if needed."

    def add_arguments(self, parser):
        parser.add_argument(
            'model_name',
            nargs='?',
            type=str,
            help='Model name (optional, case-insensitive). If omitted, all models are checked.'
        )

    def handle(self, *args, **options):
        model_name = options['model_name'].lower() if options['model_name'] else None
        models_to_check = []

        for model in apps.get_models():
            if not model_name or model.__name__.lower() == model_name:
                models_to_check.append(model)

        if not models_to_check:
            self.stdout.write(self.style.ERROR(f"❌ No matching model found for: {model_name}"))
            return

        for model in models_to_check:
            self.check_and_create(model)

    def check_and_create(self, model):
        table_name = model._meta.db_table
        self.stdout.write(self.style.NOTICE(f"🔎 Checking: {model.__name__} (table: {table_name})"))

        # --- Check if main table exists ---
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = %s
                );
            """, [table_name])
            table_exists = cursor.fetchone()[0]

        if not table_exists:
            self.stdout.write(self.style.WARNING(f"⚠️  Table '{table_name}' does not exist. Creating..."))
            with connection.schema_editor() as schema_editor:
                schema_editor.create_model(model)
            self.stdout.write(self.style.SUCCESS(f"✅ Created table '{table_name}'"))
            return

        # --- Check ManyToMany fields ---
        for field in model._meta.get_fields():
            if isinstance(field, models.ManyToManyField):
                through_model = field.remote_field.through
                through_table = through_model._meta.db_table

                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables
                            WHERE table_schema = 'public' AND table_name = %s
                        );
                    """, [through_table])
                    exists = cursor.fetchone()[0]

                if not exists:
                    self.stdout.write(self.style.WARNING(f"⚠️  M2M table '{through_table}' missing. Creating..."))
                    with connection.schema_editor() as schema_editor:
                        schema_editor.create_model(through_model)
                    self.stdout.write(self.style.SUCCESS(f"✅ Created M2M table '{through_table}'"))

        # --- Get columns from DB ---
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = %s
            """, [table_name])
            db_columns = set(row[0] for row in cursor.fetchall())

        # --- Get normal fields (skip M2M, auto-created fields) ---
        model_fields = {
            field.column: field
            for field in model._meta.get_fields()
            if hasattr(field, 'column')
            and not field.auto_created
            and not isinstance(field, models.ManyToManyField)
        }

        missing_fields = [
            (name, field) for name, field in model_fields.items()
            if name not in db_columns
        ]

        if not missing_fields:
            self.stdout.write(self.style.SUCCESS("✅ No missing fields detected."))
            return

        self.stdout.write(self.style.WARNING(f"⚠️  Missing fields: {[name for name, _ in missing_fields]}"))

        for name, field in missing_fields:
            try:
                sql = self.generate_add_column_sql(table_name, field)
                if sql:
                    with connection.cursor() as cursor:
                        cursor.execute(sql)
                    self.stdout.write(self.style.SUCCESS(f"➕ Added field '{name}'"))
                else:
                    self.stdout.write(self.style.WARNING(f"⚠️  Skipped field '{name}' (unsupported type)"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Failed to add field '{name}': {e}"))

    def generate_add_column_sql(self, table, field):
        """Generate SQL for adding a field to the table"""
        field_type = field.get_internal_type()

        type_map = {
            'CharField': f'VARCHAR({field.max_length})',
            'TextField': 'TEXT',
            'IntegerField': 'INTEGER',
            'PositiveIntegerField': 'INTEGER',
            'BigIntegerField': 'BIGINT',
            'DateTimeField': 'TIMESTAMP',
            'DateField': 'DATE',
            'BooleanField': 'BOOLEAN',
            'FloatField': 'FLOAT',
            'ImageField': 'VARCHAR(255)',
            'ForeignKey': 'INTEGER',
            'SlugField': f'VARCHAR({getattr(field, "max_length", 255) or 255})',
        }

        sql_type = type_map.get(field_type)
        if not sql_type:
            return None

        default = ''
        if isinstance(field, models.BooleanField) and field.default is not None:
            default = f'DEFAULT {field.default}'

        return f'ALTER TABLE \"{table}\" ADD COLUMN \"{field.column}\" {sql_type} {default};'
