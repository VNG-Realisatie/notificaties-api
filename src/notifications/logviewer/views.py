from django.views.generic.list import ListView

from notifications.datamodel.models import Notificatie, NotificatieResponse


class LogListView(ListView):
    template_name = 'notifications/logviewer/notificatie-list.html'
    queryset = Notificatie.objects.all().order_by('-id')
    context_object_name = 'log'

    paginate_by = 10


class ResponseLogListView(ListView):
    template_name = 'notifications/logviewer/notificatie-responses-list.html'
    context_object_name = 'log'

    paginate_by = 10

    def get_queryset(self):
        return NotificatieResponse.objects.filter(notificatie__id=self.kwargs['notificatie_id']).order_by('-id')
