# Generated by Django 3.2.13 on 2022-06-07 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("datamodel", "0024_auto_20220607_1452"),
    ]

    operations = [
        migrations.AddField(
            model_name="subscription",
            name="subscriber_reference",
            field=models.CharField(
                blank=True, max_length=255, verbose_name="Referentie subscription"
            ),
        ),
    ]
