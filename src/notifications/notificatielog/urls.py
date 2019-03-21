from django.urls import include, path

from .views import NotificatieLogListView, NotificatieResponseLogListView

app_name = 'Notificatie Log'

urlpatterns = [
    path(r'<int:notificatie_id>', NotificatieResponseLogListView.as_view(), name='notificatie_res_log'),
    path(r'', NotificatieLogListView.as_view(), name='notificatie_log'),
]
