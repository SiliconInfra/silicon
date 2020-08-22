from django.contrib import admin

from tenant.models import Tenant, TenantGroup


# Register your models here.
@admin.register(TenantGroup)
class TenantGroupAdmin(admin.ModelAdmin):
	list_display = ["name", "parent", "created_at"]
	list_filter = ["created_at"]
	readonly_fields = ["slug"]
	search_fields = ["name", "parent__name", "slug"]


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
	list_display = ["name", "group", "created_at"]
	list_filter = ["created_at"]
	readonly_fields = ["slug"]
	search_fields = ["name", "group__name", "slug"]
