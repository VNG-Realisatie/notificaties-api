import factory
import factory.fuzzy


class AbonnementFactory(factory.django.DjangoModelFactory):
    callback_url = factory.Faker('url')
    auth = factory.Sequence(lambda n: "Bearer %03d" % n)

    class Meta:
        model = 'datamodel.Abonnement'


class KanaalFactory(factory.django.DjangoModelFactory):
    naam = factory.Faker('word')
    documentatie_link = factory.Faker('url')

    class Meta:
        model = 'datamodel.Kanaal'


class FilterGroupFactory(factory.django.DjangoModelFactory):
    abonnement = factory.SubFactory(AbonnementFactory)
    kanaal = factory.SubFactory(KanaalFactory)

    class Meta:
        model = 'datamodel.FilterGroup'


class FilterFactory(factory.django.DjangoModelFactory):
    key = factory.Faker('word')
    value = factory.Faker('word')
    filter_group = factory.SubFactory(FilterGroupFactory)

    class Meta:
        model = 'datamodel.Filter'
