from django.urls import path

from .views import LogListView, ResponseLogListView

app_name = 'logviewer'

urlpatterns = [
    path(r'<int:notificatie_id>', ResponseLogListView.as_view(), name='notificatie_res_log'),
    path(r'', LogListView.as_view(), name='notificatie_log'),
]
