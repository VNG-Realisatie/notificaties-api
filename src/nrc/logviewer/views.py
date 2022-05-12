from django.db.models import Count
from django.views.generic.list import ListView

from nrc.datamodel.models import Event, EventResponse


class LogListView(ListView):
    template_name = "notifications/logviewer/notificatie-list.html"
    queryset = Event.objects.annotate(
        nr_of_subscribers=Count("eventresponse")
    ).order_by("-id")
    context_object_name = "log"

    paginate_by = 10


class ResponseLogListView(ListView):
    template_name = "notifications/logviewer/notificatie-responses-list.html"
    context_object_name = "log"

    paginate_by = 10

    def get_queryset(self):
        return EventResponse.objects.filter(event__id=self.kwargs["event_id"]).order_by(
            "-id"
        )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({"event": Event.objects.get(pk=self.kwargs["event_id"])})
        return context
