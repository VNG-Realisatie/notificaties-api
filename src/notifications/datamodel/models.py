import uuid as _uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _

import jwt

from notifications.utils.exceptions import AbonnementAuthException


class Kanaal(models.Model):
    uuid = models.UUIDField(
        unique=True, default=_uuid.uuid4,
        help_text=_('Unique resource identifier (UUID4)')
    )
    naam = models.CharField(
        _('Naam'), max_length=50, unique=True,
        help_text=_('Naam van het kanaal (ook wel "Exchange" genoemd) dat de bron vertegenwoordigd.')
    )
    documentatie_link = models.URLField(
        _('Documentatie link'), blank=True,
        help_text=_('URL naar documentatie.'),
    )
    filters = ArrayField(
        models.CharField(max_length=100),
        verbose_name=_("filters"), blank=True, default=list,
        help_text=_("Comma-separated list of filters of the kanaal")
    )

    class Meta:
        verbose_name = _('kanaal')
        verbose_name_plural = _('kanalen')

    def __str__(self) -> str:
        return f"{self.naam}"

    def match_filter_names(self, obj_filters: list) -> bool:
        if not (self.filters and obj_filters):
            return True
        for f in zip(self.filters, obj_filters):
            kanaal_filter, obj_filter = f
            if kanaal_filter != obj_filter:
                return False
        return True


class Abonnement(models.Model):
    uuid = models.UUIDField(
        unique=True, default=_uuid.uuid4,
        help_text=_('Unique resource identifier (UUID4)')
    )
    callback_url = models.URLField(
        _('Callback URL'), unique=True,
        help_text=_('De URL waar notificaties naar toe gestuurd dienen te worden. Deze URL dient uit te komen bij een '
                    'API die geschikt is om notificaties op te ontvangen.')
    )
    auth = models.CharField(
        _('Autorisatie header'), max_length=1000,
        help_text=_('Autorisatie header invulling voor het vesturen naar de "Callback URL". Voorbeeld: Bearer '
                    'a4daa31...')
    )
    client_id = models.CharField(
        _('Client ID'), max_length=100, blank=True,
        help_text=_('Client ID extracted from Auth header')
    )

    class Meta:
        verbose_name = _('abonnement')
        verbose_name_plural = _('abonnementen')

    def __str__(self) -> str:
        return f"{self.uuid}"

    @property
    def kanalen(self):
        return set([f.kanaal for f in self.filter_groups.all()])


class FilterGroup(models.Model):
    """
    link between filters, kanalen and abonnementen
    """
    abonnement = models.ForeignKey(Abonnement, on_delete=models.CASCADE, related_name='filter_groups')
    kanaal = models.ForeignKey(Kanaal, on_delete=models.CASCADE, related_name='filter_groups')

    class Meta:
        verbose_name = _('filter')
        verbose_name_plural = _('filters')

    def match_pattern(self, msg_filters):
        for f in zip(self.filters.all(), msg_filters):
            abon_filter, msg_filter = f
            msg_key = list(msg_filter)[0]
            if not (
                abon_filter.key == msg_key and (
                    abon_filter.value == '*' or abon_filter.value == msg_filter[msg_key]
                )
            ):
                return False
        return True


class Filter(models.Model):
    key = models.CharField(
        _('Sleutel'), max_length=100
    )
    value = models.CharField(
        _('Waarde'), max_length=1000
    )
    filter_group = models.ForeignKey(FilterGroup, on_delete=models.CASCADE, related_name='filters')

    def __str__(self) -> str:
        return f"{self.key}: {self.value}"

    class Meta:
        ordering = ('id', )
        verbose_name = _('filter-onderdeel')
        verbose_name_plural = _('filter-onderdelen')


class Notificatie(models.Model):
    forwarded_msg = models.TextField()
    kanaal = models.ForeignKey(Kanaal, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return 'Notificatie ({})'.format(self.kanaal)


class NotificatieResponse(models.Model):
    notificatie = models.ForeignKey(Notificatie, on_delete=models.CASCADE)
    abonnement = models.ForeignKey(Abonnement, on_delete=models.CASCADE)
    response_status = models.CharField(max_length=20, blank=True)
    exception = models.CharField(max_length=1000, blank=True)

    def __str__(self) -> str:
        return '{} {}'.format(self.abonnement, self.resultat)
