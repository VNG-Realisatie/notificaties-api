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
