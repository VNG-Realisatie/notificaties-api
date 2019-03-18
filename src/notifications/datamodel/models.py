import uuid as _uuid

from django.db import models


class Kanaal(models.Model):
    uuid = models.UUIDField(
        unique=True, default=_uuid.uuid4,
        help_text='Unique recource identifier (UUID4)'
    )
    naam = models.CharField(
        max_length=50, help_text='name of the channel/exchange',
        unique=True
    )
    documentatie_link = models.URLField(
        help_text='Url of subscriber API to which NC will post messages',
        null=True
    )

    class Mets:
        verbose_name = 'kanaal'
        verbose_name_plural = 'kanalen'

    def __str__(self) -> str:
        return f"{self.naam}"


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

    @property
    def kanalen(self):
        return set([f.kanaal for f in self.filter_groups.all()])


class FilterGroup(models.Model):
    """
    link between filters, kanalen and abonnementen
    """
    abonnement = models.ForeignKey(Abonnement, on_delete=models.CASCADE, related_name='filter_groups')
    kanaal = models.ForeignKey(Kanaal, on_delete=models.CASCADE, related_name='filter_groups')

    def match_pattern(self, msg_filters):
        abon_filters = self.filters.order_by('id')
        for f in zip(abon_filters, msg_filters):
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
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=1000)
    filter_group = models.ForeignKey(FilterGroup, on_delete=models.CASCADE, related_name='filters')
    # internal_increment = models.IntegerField(help_text="field to simplify filtering topics")

    def __str__(self) -> str:
        return f"{self.key}: {self.value}"


