from vng_api_common.filtersets import FilterSet

from nrc.datamodel.models import Domain


class DomainFilter(FilterSet):
    class Meta:
        model = Domain
        fields = ("name",)


class FilterNode:
    """
    Example filter in subscription:

    {
       "id": "....",
       "filters": [
            {
                "any": [
                    {
                        "all": [
                            {
                                "exact": {
                                    "attribute": "domain",
                                    "value": "nl.vng.zaken",
                                },
                            },
                            {
                                "any": [
                                    {
                                        "exact": {
                                            "attribute": "type",
                                            "value": "nl.vng.zaken.zaak_gesloten",
                                        },
                                    },
                                    {
                                        "exact": {
                                            "attribute": "type",
                                            "value": "nl.vng.zaken.zaak_geopend",
                                        },
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        "all": [
                            {
                                "exact": {
                                    "attribute": "domain",
                                    "value": "nl.vng.burgerzaken",
                                },
                            },
                            {
                                "exact": {
                                    "attribute": "type",
                                    "value": "nl.vng.burgerzaken.kind_geboren_aangifte_elders",
                                },
                            },
                        ],
                    },
                ],
            },
       ],
    }

    """

    def __init__(self, node):
        self.node = node

    def cast(self):
        return self

    def evaluate(self, event):
        raise NotImplementedError


class ListFilterNode(FilterNode):
    def cast(self):
        super().cast()

        if type(self.node) is not list:
            raise ValueError("Filter node should contain an array")

        filters = []

        for node in self.node:
            filter_class = FILTER_MAPPING[[*node.keys()][0]]

            for key, nested_node in node.items():
                filter = filter_class(nested_node)
                filters.append(filter.cast())

        self.filters = filters

        return self

    def __iter__(self):
        return iter(self.filters)


class AllFilterNode(ListFilterNode):
    def evaluate(self, event):
        filters = self.cast()
        return all(filter.evaluate(event) for filter in filters)


class AnyFilterNode(ListFilterNode):
    def evaluate(self, event):
        filters = self.cast()
        return any(filter.evaluate(event) for filter in filters)


class NotFilterNode(FilterNode):
    def evaluate(self, event):
        return not self.node.evaluate(event)


# TODO: case insensitive
class LeafFilterNode(FilterNode):
    def __init__(self, node):
        super().__init__(node)

    def cast(self):
        filter = super().cast()

        if not type(self.node) is dict:
            raise ValueError("Filter node is not a object")
        elif len(self.node.keys()) != 2:
            raise ValueError("Filter node should only contain two keys")
        elif self.node.keys() == ("attribute", "value"):
            raise ValueError("Filter node should only contain keys attribute and value")

        if not all(type(value) is str and value for value in self.node.values()):
            raise ValueError("Incorrect LeafFilterNode")

        return filter


class ExactFilterNode(LeafFilterNode):
    def evaluate(self, event):
        event_attribute = None
        event_data = event.forwarded_msg

        for key in event_data:
            if key.lower() == self.node["attribute"].lower():
                event_attribute = key
                break

        if not event_attribute or not type(event_data.get(event_attribute)) is str:
            return False

        return event_data[event_attribute] == self.node["value"]


class PrefixFilterNode(LeafFilterNode):
    def evaluate(self):
        raise NotImplementedError


class SuffixFilterNode(LeafFilterNode):
    def evaluate(self):
        raise NotImplementedError


FILTER_MAPPING = {
    "all": AllFilterNode,
    "any": AnyFilterNode,
    "exact": ExactFilterNode,
}


def validate_filters(data):
    filter = AllFilterNode(data)
    return filter.cast()
