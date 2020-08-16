from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


# Create your models here.
class Features(models.Model):
	name = models.CharField(max_length=20, verbose_name=_("name"))
	slug = models.SlugField(blank=True, null=True, verbose_name=_("slug"))

	class Meta:
		verbose_name = _("feature")
		verbose_name_plural = _("features")

	def __str__(self):
		return self.name


class DatacenterAuth(models.Model):
	VMWARE = "vmware"

	PROVIDER_TYPES = [
		(VMWARE, _("vmware"))
	]

	hostname = models.CharField(max_length=100, verbose_name=_("hostname"), unique=True)
	username = models.CharField(max_length=20, verbose_name=_("username"))
	password = models.CharField(max_length=20, verbose_name=_("password"))
	secure_ssl = models.BooleanField(default=True, verbose_name=_("secure ssl"))
	provider = models.CharField(max_length=20, choices=PROVIDER_TYPES, default="vmware")
	created_at = models.DateTimeField(default=timezone.now, verbose_name=_("created at"))

	class Meta:
		verbose_name = _("authentication")
		verbose_name_plural = _("authentication")

	def __str__(self):
		return self.hostname


class Cluster(models.Model):
	name = models.CharField(max_length=64, verbose_name=_("name"))

	class Meta:
		verbose_name = _("cluster")
		verbose_name_plural = _("clusters")

	def __str__(self):
		return self.name


class Datacenter(models.Model):
	name = models.CharField(max_length=20, verbose_name=_("name"))
	slug = models.SlugField(blank=True, null=True, verbose_name=_("slug"))
	features = models.ManyToManyField(to=Features, verbose_name=_("features"))
	cluster = models.ManyToManyField(to=Cluster, verbose_name=_("cluster"))
	authentication = models.ForeignKey(to=DatacenterAuth, verbose_name=_("authentication"), on_delete=models.SET_NULL,
	                                   null=True)

	class Meta:
		verbose_name = _("datacenter")
		verbose_name_plural = _("datacenters")

	def __str__(self):
		return self.name


class Region(models.Model):
	name = models.CharField(max_length=20, verbose_name=_("name"))
	slug = models.SlugField(blank=True, null=True, verbose_name=_("slug"))
	datacenter = models.ManyToManyField(to=Datacenter, verbose_name=_("datacenter"))

	class Meta:
		verbose_name = _("region")
		verbose_name_plural = _("regions")

	def __str__(self):
		return self.name
