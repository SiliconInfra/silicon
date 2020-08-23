from django.contrib import admin

from inventory.models import Cable, Device, DeviceRole, DeviceType, Manufacturer, Platform


# Register your models here.
@admin.register(Cable)
class CableAdmin(admin.ModelAdmin):
	list_display = ["termination_a", "termination_b", "type", "status", "label", "color", "length", "length_unit"]
	list_filter = ["type", "status"]
	search_fields = ["label"]


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
	list_display = ["name", "slug"]
	search_fields = ["name"]
	readonly_fields = ["slug"]


@admin.register(DeviceType)
class DeviceTypeAdmin(admin.ModelAdmin):
	readonly_fields = ["slug"]
	list_display = ["model", "manufacturer", "part_number", "u_height", "is_full_depth"]
	list_filter = ["manufacturer__name", "u_height", "is_full_depth"]
	search_fields = ["manufacturer__name", "model", "part_number"]


@admin.register(DeviceRole)
class DeviceRoleAdmin(admin.ModelAdmin):
	readonly_fields = ["slug"]
	list_display = ["name", "color", "vm_role"]
	list_filter = ["color", "vm_role"]
	search_fields = ["name", "slug"]


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
	readonly_fields = ["slug"]
	list_display = ["name", "manufacturer"]
	list_filter = ["manufacturer__name"]
	search_fields = ["name", "manufacturer__name"]


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
	list_display = ["name", "device_type", "device_role", "platform", "serial", "position", "face", "status"]
	list_filter = ["device_type", "device_role", "platform", "position", "face", "status"]
	search_fields = ["name"]
