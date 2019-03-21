from django.shortcuts import render
from django.views.generic.list import ListView

from notifications.datamodel.models import Notificatie, NotificatieResponse


class NotificatieLogListView(ListView):
    template_name = 'notificatie-list.html'
    queryset = Notificatie.objects.all().order_by('id')
    context_object_name = 'log'

    paginate_by = 10


class NotificatieResponseLogListView(ListView):
    template_name = 'notificatie-responses-list.html'
    context_object_name = 'log'

    paginate_by = 10

    def get_queryset(self):
        return NotificatieResponse.objects.filter(notificatie__id=self.kwargs['notificatie_id']).order_by('id')
