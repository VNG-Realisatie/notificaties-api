from django.urls import path

from .views import LogListView, ResponseLogListView

app_name = "logviewer"

urlpatterns = [
    path(
        r"<int:event_id>",
        ResponseLogListView.as_view(),
        name="event_res_log",
    ),
    path(r"", LogListView.as_view(), name="event_log"),
]
