# Generated by Django 3.2.13 on 2022-06-09 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("datamodel", "0030_auto_20220608_1421"),
    ]

    operations = [
        migrations.AddField(
            model_name="subscription",
            name="filters",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
