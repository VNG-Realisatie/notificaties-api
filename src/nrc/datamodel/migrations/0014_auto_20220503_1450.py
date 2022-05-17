# Generated by Django 3.2.13 on 2022-05-03 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("datamodel", "0013_auto_20220503_1433"),
    ]

    operations = [
        migrations.AlterField(
            model_name="subscription",
            name="config",
            field=models.JSONField(
                help_text="Implementatie specifieke instellingen gebruikt door de abbonements manager om voor het vergaren van notificaties.",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="protocol_settings",
            field=models.JSONField(
                help_text="Instellingen voor het aflever protocol.", null=True
            ),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="sink_credentials",
            field=models.JSONField(
                help_text="Toegangsgegevens voor het opgegeven address.",
                null=True,
                verbose_name="Sink toegangsgegevens",
            ),
        ),
    ]