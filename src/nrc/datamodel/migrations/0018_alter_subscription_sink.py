# Generated by Django 3.2.13 on 2022-05-31 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("datamodel", "0017_auto_20220531_0923"),
    ]

    operations = [
        migrations.AlterField(
            model_name="subscription",
            name="sink",
            field=models.URLField(
                help_text="Het address waarnaar NOTIFICATIEs afgeleverd worden via het opgegeven protocol."
            ),
        ),
    ]
