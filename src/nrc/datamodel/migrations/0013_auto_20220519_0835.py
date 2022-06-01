# Generated by Django 3.2.13 on 2022-05-19 08:35

import django.contrib.postgres.fields
import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("datamodel", "0012_auto_20190605_1523"),
    ]

    operations = [
        migrations.CreateModel(
            name="Domain",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Naam van het DOMAIN dat de bron vertegenwoordigd.",
                        max_length=255,
                        unique=True,
                        verbose_name="Naam",
                    ),
                ),
                (
                    "documentation_link",
                    models.URLField(
                        blank=True,
                        help_text="URL naar documentatie.",
                        verbose_name="Documentatie link",
                    ),
                ),
            ],
            options={
                "verbose_name": "domain",
                "verbose_name_plural": "domains",
            },
        ),
        migrations.CreateModel(
            name="Event",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "forwarded_msg",
                    models.JSONField(
                        encoder=django.core.serializers.json.DjangoJSONEncoder
                    ),
                ),
                (
                    "domain",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="datamodel.domain",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="EventResponse",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("exception", models.CharField(blank=True, max_length=1000)),
                ("response_status", models.IntegerField(null=True)),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="datamodel.event",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Subscription",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        help_text="Unique resource identifier (UUID4)",
                        unique=True,
                    ),
                ),
                (
                    "protocol",
                    models.CharField(
                        default="HTTP",
                        help_text="Identificatie van het aflever protocol.",
                        max_length=255,
                    ),
                ),
                (
                    "protocol_settings",
                    models.JSONField(
                        help_text="Instellingen voor het aflever protocol.", null=True
                    ),
                ),
                (
                    "sink",
                    models.CharField(
                        help_text="Het address waarnaar NOTIFICATIEs afgeleverd worden via het opgegeven protocol.",
                        max_length=255,
                    ),
                ),
                (
                    "sink_credential",
                    models.JSONField(
                        help_text="Toegangsgegevens voor het opgegeven address.",
                        null=True,
                        verbose_name="Sink toegangsgegevens",
                    ),
                ),
                (
                    "config",
                    models.JSONField(
                        help_text="Implementatie specifieke instellingen gebruikt door de abbonements manager om voor het vergaren van notificaties.",
                        null=True,
                    ),
                ),
                (
                    "source",
                    models.CharField(
                        help_text="Bron van dit abonnement.", max_length=255
                    ),
                ),
                (
                    "types",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=255),
                        blank=True,
                        help_text="Notificaties types relevant voor afleveren voor dit abonnement.",
                        null=True,
                        size=None,
                    ),
                ),
                (
                    "domain",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="domains",
                        to="datamodel.domain",
                        verbose_name="Domain",
                    ),
                ),
            ],
            options={
                "verbose_name": "subscription",
                "verbose_name_plural": "subscriptions",
            },
        ),
        migrations.RemoveField(
            model_name="filter",
            name="filter_group",
        ),
        migrations.RemoveField(
            model_name="filtergroup",
            name="abonnement",
        ),
        migrations.RemoveField(
            model_name="filtergroup",
            name="kanaal",
        ),
        migrations.RemoveField(
            model_name="notificatie",
            name="kanaal",
        ),
        migrations.RemoveField(
            model_name="notificatieresponse",
            name="abonnement",
        ),
        migrations.RemoveField(
            model_name="notificatieresponse",
            name="notificatie",
        ),
        migrations.DeleteModel(
            name="Abonnement",
        ),
        migrations.DeleteModel(
            name="Filter",
        ),
        migrations.DeleteModel(
            name="FilterGroup",
        ),
        migrations.DeleteModel(
            name="Kanaal",
        ),
        migrations.DeleteModel(
            name="Notificatie",
        ),
        migrations.DeleteModel(
            name="NotificatieResponse",
        ),
        migrations.AddField(
            model_name="eventresponse",
            name="subscription",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="datamodel.subscription"
            ),
        ),
    ]
