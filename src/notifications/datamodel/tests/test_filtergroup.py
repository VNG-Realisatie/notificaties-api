import uuid

from django.test import TestCase

from .factories import FilterGroupFactory, FilterFactory


class FilterGroupTests(TestCase):

    def test_match_pattern_true_same_length(self):
        """
        Test match_pattern method:
        Assert it if filters in message and in abonnement data match
        """

        filter_group = FilterGroupFactory.create()
        filter1 = FilterFactory.create(filter_group=filter_group, key='bron', value='082096752011')
        filter2 = FilterFactory.create(filter_group=filter_group, key='zaaktype', value='example.com/api/v1')
        filter3 = FilterFactory.create(filter_group=filter_group, key='vertrouwelijkeidaanduiding', value='*')
        msg_filters = [
            {"bron": "082096752011"},
            {"zaaktype": "example.com/api/v1"},
            {"vertrouwelijkeidaanduiding": "openbaar"}
        ]

        match = filter_group.match_pattern(msg_filters)

        self.assertTrue(match)

    def test_match_pattern_true_different_length(self):
        """
        Test match_pattern method:
        Assert it if filters in message and in abonnement data match
        """

        filter_group = FilterGroupFactory.create()
        filter1 = FilterFactory.create(filter_group=filter_group, key='bron', value='082096752011')
        msg_filters = [
            {"bron": "082096752011"},
            {"zaaktype": "example.com/api/v1"},
            {"vertrouwelijkeidaanduiding": "openbaar"}
        ]

        match = filter_group.match_pattern(msg_filters)

        self.assertTrue(match)

    def test_match_pattern_false_keys(self):
        """
        Test match_pattern method:
        Assert it if filters in message and in abonnement filter names don't match
        """
        filter_group = FilterGroupFactory.create()
        filter1 = FilterFactory.create(filter_group=filter_group, key='bron', value='082096752011')
        filter2 = FilterFactory.create(filter_group=filter_group, key='zaaktype', value='example.com/api/v1')
        filter3 = FilterFactory.create(filter_group=filter_group, key='vertrouwelijkeidaanduiding', value='*')
        msg_filters = [
            {"bron": "082096752011"},
            {"objecttype": "example.com/api/v1"},
            {"vertrouwelijkeidaanduiding": "openbaar"}
        ]

        match = filter_group.match_pattern(msg_filters)

        self.assertFalse(match)

    def test_match_pattern_false_values(self):
        """
        Test match_pattern method:
        Assert it if filters in message and in abonnement filter values don't match
        """
        filter_group = FilterGroupFactory.create()
        filter1 = FilterFactory.create(filter_group=filter_group, key='bron', value='082096752011')
        filter2 = FilterFactory.create(filter_group=filter_group, key='zaaktype', value='example.com/api/v1')
        filter3 = FilterFactory.create(filter_group=filter_group, key='vertrouwelijkeidaanduiding', value='*')
        msg_filters = [
            {"bron": "13"},
            {"zaaktype": "example.com/api/v1"},
            {"vertrouwelijkeidaanduiding": "openbaar"}
        ]

        match = filter_group.match_pattern(msg_filters)

        self.assertFalse(match)
