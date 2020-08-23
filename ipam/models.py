import netaddr
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from inventory.models import Device
from ipam.constants import VRF_RD_MAX_LENGTH
from ipam.enums import IPAddressStatusChoices, PrefixStatusChoices, ServiceProtocolChoices, VLANStatusChoices


# Create your models here.
class VRF(models.Model):
	name = models.CharField(max_length=20, verbose_name=_("name"))
	rd = models.CharField(max_length=VRF_RD_MAX_LENGTH, unique=True, blank=True, null=True,
	                      verbose_name=_("route distinguisher"))
	enforce_unique = models.BooleanField(default=True, verbose_name=_("enforce unique"))
	description = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("description"))

	class Meta:
		verbose_name = _("VRF")
		verbose_name_plural = _("VRFs")

	def __str__(self):
		return self.name


class RIR(models.Model):
	name = models.CharField(max_length=20, verbose_name=_("name"))
	is_private = models.BooleanField(default=False, verbose_name=_("is private"))
	description = models.CharField(max_length=200, blank=True, verbose_name=_("description"))

	class Meta:
		verbose_name = _("RIR")
		verbose_name_plural = _("RIRs")

	def __str__(self):
		return self.name


class Aggregate(models.Model):
	prefix = models.GenericIPAddressField(verbose_name=_("prefix"))
	rir = models.ForeignKey(to=RIR, on_delete=models.PROTECT, related_name="aggregates")
	description = models.CharField(max_length=200, blank=True, verbose_name=_("description"))

	class Meta:
		verbose_name = _("aggregate")
		verbose_name_plural = _("aggregates")

	def __str__(self):
		return self.prefix


class IPAddress(models.Model):
	address = models.GenericIPAddressField(verbose_name=_("ip address"))
	vrf = models.ForeignKey(to=VRF, on_delete=models.PROTECT, verbose_name=_("VRF"), related_name="ip_addresses",
	                        blank=True, null=True)
	status = models.CharField(max_length=50, choices=IPAddressStatusChoices.choices(),
	                          default=IPAddressStatusChoices.STATUS_ACTIVE.value, verbose_name=_("status"))
	assigned_object_type = models.ForeignKey(to=ContentType, on_delete=models.PROTECT, related_name='+', blank=True,
	                                         null=True, verbose_name=_("assigned object type"))
	assigned_object_id = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("assigned object id"))
	assigned_object = GenericForeignKey(ct_field="assigned_object_type", fk_field="assigned_object_id")
	nat_inside = models.OneToOneField(to="self", on_delete=models.SET_NULL, related_name='nat_outside', blank=True,
	                                  null=True, verbose_name=_("nat inside"))
	dns_name = models.CharField(max_length=255, blank=True, verbose_name=_("dns name"))
	description = models.CharField(max_length=200, blank=True, verbose_name=_("description"))

	class Meta:
		verbose_name = _("ip address")
		verbose_name_plural = _("ip addresses")

	def __str__(self):
		return self.address

	def save(self, *args, **kwargs):
		# Force dns_name to lowercase
		self.dns_name = self.dns_name.lower()

		super().save(*args, **kwargs)


class VLANGroup(models.Model):
	name = models.CharField(max_length=50, verbose_name=_("name"))
	description = models.CharField(max_length=200, blank=True, verbose_name=_("description"))

	class Meta:
		verbose_name = _("vlan group")
		verbose_name_plural = _("vlan groups")

	def __str__(self):
		return self.name

	def get_next_available_vid(self):
		"""
		Return the first available VLAN ID (1-4094) in the group.
		"""
		vlan_ids = VLAN.objects.filter(group=self).values_list('vid', flat=True)
		for i in range(1, 4095):
			if i not in vlan_ids:
				return i
		return None


class VLAN(models.Model):
	group = models.ForeignKey(to=VLANGroup, on_delete=models.PROTECT, related_name='vlans', blank=True, null=True,
	                          verbose_name=_("group"))
	vid = models.PositiveSmallIntegerField(verbose_name=_("vlan id"))
	name = models.CharField(max_length=64, verbose_name=_("name"))
	status = models.CharField(max_length=50, choices=VLANStatusChoices.choices(), verbose_name=_("status"),
	                          default=VLANStatusChoices.STATUS_ACTIVE.value)
	description = models.CharField(max_length=200, blank=True, verbose_name=_("description"))

	class Meta:
		verbose_name = _("VLAN")
		verbose_name_plural = _("VLANs")

	def __str__(self):
		return self.name


class Service(models.Model):
	device = models.ForeignKey(to=Device, on_delete=models.CASCADE, related_name='services', null=True, blank=True,
	                           verbose_name=_("device"))
	name = models.CharField(max_length=30, verbose_name=_("name"))
	protocol = models.CharField(max_length=50, choices=ServiceProtocolChoices.choices())
	port = models.PositiveIntegerField(verbose_name=_("port number"))
	addresses = models.ManyToManyField(to=IPAddress, related_name='services', blank=True,
	                                   verbose_name=_("ip addresses"))
	description = models.CharField(max_length=200, blank=True, verbose_name=_("description"))

	class Meta:
		verbose_name = _("service")
		verbose_name_plural = _("services")

	def __str__(self):
		return self.name

	@property
	def parent(self):
		return self.device

	def clean(self):
		if not self.device:
			raise ValidationError("A service must be associated with a device")


class Prefix(models.Model):
	prefix = models.GenericIPAddressField(verbose_name=_("prefix"))
	vrf = models.ForeignKey(to=VRF, on_delete=models.PROTECT, verbose_name=_("VRF"), related_name="prefixes",
	                        blank=True, null=True)
	vlan = models.ForeignKey(to=VLAN, on_delete=models.PROTECT, verbose_name=_("vlan"), related_name="prefixes",
	                         blank=True, null=True)
	status = models.CharField(max_length=20, choices=PrefixStatusChoices.choices(),
	                          default=PrefixStatusChoices.STATUS_ACTIVE.value, verbose_name=_("status"))
	is_pool = models.BooleanField(verbose_name=_("is pool"), default=False)
	description = models.CharField(max_length=200, blank=True, verbose_name=_("description"))

	class Meta:
		verbose_name = _("prefix")
		verbose_name_plural = _("prefixes")

	def __str__(self):
		return self.prefix

	def save(self, *args, **kwargs):
		if isinstance(self.prefix, netaddr.IPNetwork):
			# Clear host bits from prefix
			self.prefix = self.prefix.cidr

		super().save(*args, **kwargs)
