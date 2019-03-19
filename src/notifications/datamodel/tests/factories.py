import factory
import factory.fuzzy


class AbonnementFactory(factory.django.DjangoModelFactory):
    callback_url = factory.Faker('url')
    auth = 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImNsaWVudF9pZGVudGlmaWVyIjoienJjIn0.eyJpc3MiOiJ6cmMiLCJpYXQiOjE1NTI5OTM4MjcsInpkcyI6eyJzY29wZXMiOlsiemRzLnNjb3Blcy56YWtlbi5hYW5tYWtlbiJdLCJ6YWFrdHlwZXMiOlsiaHR0cDovL3p0Yy5ubC9hcGkvdjEvemFha3R5cGUvMTIzNCJdfX0.NHcWwoRYMuZ5IoUAWUs2lZFxLVLGhIDnU_LWTjyGCD4'

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
