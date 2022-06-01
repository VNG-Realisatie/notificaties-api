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
                    {
                      "any": [
                        {
                          "exact": {
                            "attribute": "domain",
                            "value": "nl.vng.zaken",
                           },
                        },
                        {
                          "exact": {
                            "attribute": "type",
                            "value": "nl.vng.zaken.zaak_gesloten",
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
                      "value": "nl.vng.zaken",
                     },
                  },
                  {
                    "exact": {
                      "attribute": "type",
                      "value": "nl.vng.zaken.zaak_gesloten",
                     },
                  },
                ],
               },
                ],
              },
            ],
          },
       ],
    }

    """

    def __init__(self, event):
        self.event = event

    def evaluate(self):
        raise NotImplementedError


# This is always the first filter to be used
class AllFilterNode(FilterNode):
    def __init__(self, nodes):
        self.nodes = nodes

    def evaluate(self):
        return all(node.evaluate() for node in self.nodes)


class AnyFilterNode(FilterNode):
    def __init__(self, nodes):
        self.nodes = nodes

    def evaluate(self):
        return any(node.evaluate() for node in self.nodes)


class NotFilterNode(FilterNode):
    def __init__(self, node):
        self.node = node

    def evaluate(self):
        return not self.node.evaluate()


# TODO: evaluate False if value is not string
# TODO: case insensitive
class LeafFilterNode(FilterNode):
    def __init__(self, attribute, value, event):
        super().__init__(event)

        self.attribute = attribute
        self.value = value


class ExactFilterNode(LeafFilterNode):
    def evaluate(self):
        if not self.attribute in self.event:
            return False

        return self.event.get(self.attribute) == self.value


class PrefixFilterNode(LeafFilterNode):
    def evaluate(self):
        raise NotImplementedError


class SuffixFilterNode(LeafFilterNode):
    def evaluate(self):
        raise NotImplementedError
