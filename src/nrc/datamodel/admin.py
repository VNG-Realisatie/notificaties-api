from django.contrib import admin

from .models import Domain, Event, Subscription

# TODO: add NotificatieResponse admin?


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("uuid", "sink", "source", "domain")
    readonly_fields = ("uuid",)
    list_filter = ("domain",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("__str__",)

    list_filter = ("domain",)
    search_fields = ("domain", "forwarded_msg")
