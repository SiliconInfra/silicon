from django.contrib import admin

from datacenter.models import Cluster, Datacenter, DatacenterAuth, Features, Region


# Register your models here.

@admin.register(Features)
class FeaturesAdmin(admin.ModelAdmin):
	list_display = ["name"]
	search_fields = ["name"]


@admin.register(DatacenterAuth)
class DatacenterAuthAdmin(admin.ModelAdmin):
	list_display = ["hostname", "username", "provider", "secure_ssl"]
	list_filter = ["provider", "secure_ssl", "created_at"]
	search_fields = ["hostname"]


@admin.register(Datacenter)
class DatacenterAdmin(admin.ModelAdmin):
	list_display = ["name", "cluster_list", "feature_list"]
	search_fields = ["name"]
	list_filter = ["features"]

	def cluster_list(self, obj):
		return ", ".join([o.name for o in obj.cluster.all()])

	def feature_list(self, obj):
		return ", ".join([o.name for o in obj.features.all()])

	feature_list.short_description = "Features"


@admin.register(Cluster)
class ClusterAdmin(admin.ModelAdmin):
	list_display = ["name"]


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
	list_display = ["name", "datacenter_list"]
	search_fields = ["name"]

	def datacenter_list(self, obj):
		return ", ".join([o.name for o in obj.datacenter.all()])

	datacenter_list.short_description = "Datacenters"
