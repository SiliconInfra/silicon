from django.contrib import admin

from ipam.models import Aggregate, IPAddress, Prefix, RIR, Service, VLAN, VLANGroup, VRF


# Register your models here.

@admin.register(VRF)
class VRFAdmin(admin.ModelAdmin):
	list_display = ["name", "rd", "enforce_unique"]
	search_fields = ["name"]
	list_filter = ["enforce_unique"]


@admin.register(RIR)
class RIRAdmin(admin.ModelAdmin):
	list_display = ["name", "is_private"]
	search_fields = ["name"]
	list_filter = ["is_private"]


@admin.register(Aggregate)
class AggregateAdmin(admin.ModelAdmin):
	list_display = ["prefix", "rir"]


@admin.register(Prefix)
class PrefixAdmin(admin.ModelAdmin):
	list_display = ["prefix", "vrf", "vlan", "status", "is_pool"]
	list_filter = ["status", "is_pool"]
	search_fields = ["vrf__name", "vlan__name", "vlan__id"]


@admin.register(IPAddress)
class IPAddressAdmin(admin.ModelAdmin):
	list_display = ["address", "vrf", "status", "assigned_object", "nat_inside", "dns_name"]
	list_filter = ["status"]
	search_fields = ["vrf__name", "address"]


@admin.register(VLANGroup)
class VLANGroupAdmin(admin.ModelAdmin):
	list_display = ["name"]
	search_fields = ["name"]


@admin.register(VLAN)
class VLANAdmin(admin.ModelAdmin):
	list_display = ["group", "vid", "name", "status"]
	list_filter = ["status", "group"]
	search_fields = ["name", "vid", "group__name"]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
	list_display = ["name", "device", "protocol", "port", "ip_addresses"]
	list_filter = ["device__name", "protocol"]
	search_fields = ["name", "addresses__address"]

	def ip_addresses(self, obj):
		return ", ".join([o.address for o in obj.addresses.all()])

	ip_addresses.short_description = "IP Addresses"
