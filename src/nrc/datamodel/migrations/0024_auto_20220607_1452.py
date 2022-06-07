# Generated by Django 3.2.13 on 2022-06-07 14:52

import uuid

from django.db import migrations, models

import django_better_admin_arrayfield.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ("datamodel", "0023_alter_domain_filter_attributes"),
    ]

    operations = [
        migrations.AddField(
            model_name="domain",
            name="uuid",
            field=models.UUIDField(
                default=uuid.uuid4,
                help_text="Unique resource identifier (UUID4)",
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="types",
            field=django_better_admin_arrayfield.models.fields.ArrayField(
                base_field=models.CharField(max_length=255),
                blank=True,
                default=list,
                help_text="Notificaties types relevant voor afleveren voor dit abonnement.",
                size=None,
            ),
        ),
    ]