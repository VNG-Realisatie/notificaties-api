# Generated by Django 3.2.13 on 2022-06-08 10:10

from django.db import migrations, models

import django_better_admin_arrayfield.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ("datamodel", "0027_auto_20220608_1009"),
    ]

    operations = [
        migrations.AlterField(
            model_name="subscription",
            name="types",
            field=django_better_admin_arrayfield.models.fields.ArrayField(
                base_field=models.CharField(max_length=255),
                blank=True,
                help_text="Notificaties types relevant voor afleveren voor dit abonnement.",
                null=True,
                size=None,
            ),
        ),
    ]