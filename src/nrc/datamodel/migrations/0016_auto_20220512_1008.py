# Generated by Django 3.2.13 on 2022-05-12 10:08

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("datamodel", "0015_rename_sink_credentials_subscription_sink_credential"),
    ]

    operations = [
        migrations.AlterField(
            model_name="domain",
            name="name",
            field=models.CharField(
                help_text="Naam van het DOMAIN dat de bron vertegenwoordigd.",
                max_length=255,
                unique=True,
                verbose_name="Naam",
            ),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="types",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=255),
                blank=True,
                help_text="Notificaties types relevant voor afleveren voor dit abonnement.",
                null=True,
                size=None,
            ),
        ),
    ]
