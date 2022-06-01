from django.contrib import admin

from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin

from .models import Domain, Event, EventResponse, Subscription


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin, DynamicArrayMixin):
    list_display = (
        "name",
        "created_on",
        "last_updated",
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin, DynamicArrayMixin):
    list_display = ("uuid", "sink", "source", "domain")
    readonly_fields = ("uuid",)
    list_filter = ("domain",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "created_on",
    )

    list_filter = ("domain",)
    search_fields = ("domain", "forwarded_msg")


@admin.register(EventResponse)
class EventResponseAdmin(admin.ModelAdmin):
    list_display = (
        "event",
        "subscription",
        "response_status",
    )
    readonly_fields = (
        "event",
        "subscription",
        "exception",
        "response_status",
    )
