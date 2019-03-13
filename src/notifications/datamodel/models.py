import uuid as _uuid

from django.db import models


class Abonnement(models.Model):
    uuid = models.UUIDField(
        unique=True, default=_uuid.uuid4,
        help_text='Unique recource identifier (UUID4)'
    )
    callback_url = models.URLField(
        help_text='Url of subscriber API to which NC will post messages',
        unique=True
    )
    auth = models.CharField(
        max_length=1000, blank=True,
        help_text='Authentication method to subscriber'
    )

    class Meta:
        verbose_name = 'abonnement'
        verbose_name_plural = 'abonnementen'


class Kanaal(models.Model):
    uuid = models.UUIDField(
        unique=True, default=_uuid.uuid4,
        help_text='Unique recource identifier (UUID4)'
    )
    naam = models.CharField(max_length=50, help_text='name of the channel/exchange')
    abonnement = models.ForeignKey(
        Abonnement, on_delete=models.SET_NULL,
        related_name='kanalen', null=True)

    class Mets:
        verbose_name = 'kanaal'
        verbose_name_plural = 'kanalen'


class Filter(models.Model):
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=1000)
    kanaal = models.ForeignKey(Kanaal, on_delete=models.CASCADE, related_name='filters')

    def __str__(self) -> str:
        return f"{self.key}: {self.value}"



