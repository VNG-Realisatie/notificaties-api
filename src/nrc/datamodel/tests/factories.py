import factory
import factory.fuzzy


class SubscriptionFactory(factory.django.DjangoModelFactory):
    domain = factory.SubFactory("nrc.datamodel.tests.factories.DomainFactory")
    types = factory.List(
        [
            "Type A",
            "Type B",
        ]
    )

    class Meta:
        model = "datamodel.Subscription"


class DomainFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("word")
    documentation_link = factory.Faker("url")

    class Meta:
        model = "datamodel.Domain"


class EventFactory(factory.django.DjangoModelFactory):
    forwarded_msg = factory.Faker("text", max_nb_chars=1000)
    domain = factory.SubFactory(DomainFactory)

    class Meta:
        model = "datamodel.Event"
