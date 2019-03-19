from django.conf.urls import url
from django.urls import include, path

from vng_api_common import routers
from vng_api_common.schema import SchemaView

from .viewsets import AbonnementViewSet, KanaalViewSet, NotificatieAPIView

router = routers.DefaultRouter()
router.register('abonnement', AbonnementViewSet)
router.register('kanaal', KanaalViewSet)


urlpatterns = [
    url(r'^v(?P<version>\d+)/', include([

        # API documentation
        url(r'^schema/openapi(?P<format>\.json|\.yaml)$',
            SchemaView.without_ui(cache_timeout=None),
            name='schema-json'),
        url(r'^schema/$',
            SchemaView.with_ui('redoc', cache_timeout=None),
            name='schema-redoc'),

        # actual API
        url(r'^notificaties', NotificatieAPIView.as_view(), name='notificaties'),
        url(r'^', include(router.urls)),

        # should not be picked up by drf-yasg
        path('', include('vng_api_common.api.urls')),
    ])),
]
