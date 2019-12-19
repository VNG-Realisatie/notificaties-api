from django.core.management import call_command
from django.db import migrations


def forward(apps, schema_editor):
    from django.apps import apps as django_apps
    from django.contrib.contenttypes.management import create_contenttypes

    apps = django_apps.get_app_configs()
    for app in apps:
        create_contenttypes(app)

    call_command("loaddata", "default_admin_index.json")


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
        ("admin_index", "0002_auto_20170802_1754"),
        ("datamodel", "0012_auto_20190605_1523"),
    ]

    operations = [migrations.RunPython(forward, migrations.RunPython.noop)]
