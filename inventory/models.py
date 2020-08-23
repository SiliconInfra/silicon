from colorfield.fields import ColorField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from slugify import slugify

from inventory.enums import CableLengthUnit, CableStatus, CableTypes, DeviceFaceChoices, DeviceStatusChoices


# Create your models here.
class Cable(models.Model):
	termination_a_type = models.ForeignKey(to=ContentType, on_delete=models.PROTECT, related_name="+",
	                                       verbose_name=_("termination a type"))
	termination_a_id = models.PositiveIntegerField()
	termination_a = GenericForeignKey(ct_field="termination_a_type", fk_field="termination_a_id")
	termination_b_type = models.ForeignKey(to=ContentType, on_delete=models.PROTECT, related_name="+",
	                                       verbose_name=_("termination b type"))
	termination_b_id = models.PositiveIntegerField()
	termination_b = GenericForeignKey(ct_field="termination_b_type", fk_field="termination_b_id")
	type = models.CharField(max_length=50, choices=CableTypes.choices(), blank=True, verbose_name=_("type"))
	status = models.CharField(max_length=50, choices=CableStatus.choices(), default=CableStatus.STATUS_CONNECTED.value,
	                          verbose_name=_("status"))
	label = models.CharField(max_length=100, blank=True, verbose_name=_("label"))
	color = ColorField(verbose_name=_("color"), blank=True)
	length = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("length"))
	length_unit = models.CharField(max_length=20, choices=CableLengthUnit.choices(), blank=True,
	                               verbose_name=_("length unit"))

	class Meta:
		verbose_name = _("cable")
		verbose_name_plural = _("cables")

	def __str__(self):
		return self.label or '#{}'.format(self.pk)

	def clean(self):
		# A termination point cannot be connected to itself
		if self.termination_a == self.termination_b:
			raise ValidationError(f"Cannot connect {self.termination_a_type} to itself")


class Manufacturer(models.Model):
	name = models.CharField(max_length=100, unique=True, verbose_name=_("name"))
	slug = models.SlugField(unique=True, verbose_name=_("slug"))
	description = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("description"))

	class Meta:
		verbose_name = _("manufacturer")
		verbose_name_plural = _("manufacturers")
		ordering = ["name"]

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = self.create_slug(self.name)
		self.full_clean()
		super(Manufacturer, self).save(*args, **kwargs)

	@staticmethod
	def create_slug(name):
		slug = slugify(name)
		return slug[:50]


class DeviceType(models.Model):
	manufacturer = models.ForeignKey(to=Manufacturer, on_delete=models.PROTECT, related_name="device_types",
	                                 verbose_name=_("manufacturer"))
	model = models.CharField(max_length=100, verbose_name=_("model"))
	slug = models.SlugField(unique=True, verbose_name=_("slug"))
	part_number = models.CharField(max_length=50, blank=True, verbose_name=_("part number"))
	u_height = models.PositiveIntegerField(default=1, verbose_name=_("height"))
	is_full_depth = models.BooleanField(default=True, verbose_name=_("full depth"))
	front_image = models.ImageField(upload_to="device-type", blank=True, verbose_name=_("front image"))
	rear_image = models.ImageField(upload_to="device-type", blank=True, verbose_name=_("rear image"))

	class Meta:
		verbose_name = _("device type")
		verbose_name_plural = _("device types")
		unique_together = [["manufacturer", "model"], ["manufacturer", "slug"]]

	def __str__(self):
		return self.model

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = self.create_slug(self.model)
		self.full_clean()
		super(DeviceType, self).save(*args, **kwargs)

	@staticmethod
	def create_slug(name):
		slug = slugify(name)
		return slug[:50]

	@property
	def display_name(self):
		return f'{self.manufacturer.name} {self.model}'


class DeviceRole(models.Model):
	name = models.CharField(max_length=100, verbose_name=_("name"))
	slug = models.SlugField(unique=True, verbose_name=_("slug"))
	color = ColorField(verbose_name=_("color"))
	vm_role = models.BooleanField(default=True, verbose_name=_("vm role"))
	description = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("description"))

	class Meta:
		verbose_name = _("device role")
		verbose_name_plural = _("device roles")

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = self.create_slug(self.name)
		self.full_clean()
		super(DeviceRole, self).save(*args, **kwargs)

	@staticmethod
	def create_slug(name):
		slug = slugify(name)
		return slug[:50]


class Platform(models.Model):
	name = models.CharField(max_length=100, verbose_name=_("name"))
	slug = models.SlugField(unique=True, verbose_name=_("slug"))
	description = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("description"))
	manufacturer = models.ForeignKey(to=Manufacturer, on_delete=models.PROTECT, related_name="platforms",
	                                 verbose_name=_("manufacturer"))

	class Meta:
		verbose_name = _("platform")
		verbose_name_plural = _("platforms")
		ordering = ["name"]

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = self.create_slug(self.name)
		self.full_clean()
		super(Platform, self).save(*args, **kwargs)

	@staticmethod
	def create_slug(name):
		slug = slugify(name)
		return slug[:50]


class Device(models.Model):
	name = models.CharField(max_length=100, verbose_name=_("name"))
	device_type = models.ForeignKey(to=DeviceType, on_delete=models.PROTECT, related_name="instances",
	                                verbose_name=_("device type"))
	device_role = models.ForeignKey(to=DeviceRole, on_delete=models.PROTECT, related_name="devices",
	                                verbose_name=_("device role"))
	platform = models.ForeignKey(to=Platform, on_delete=models.SET_NULL, verbose_name=_("platform"),
	                             related_name="devices", blank=True, null=True)
	serial = models.CharField(max_length=100, verbose_name=_("serial"))
	position = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=_("position"))
	face = models.CharField(max_length=50, blank=True, choices=DeviceFaceChoices.choices(), verbose_name=_("rack face"))
	status = models.CharField(max_length=50, choices=DeviceStatusChoices.choices(), verbose_name=_("status"),
	                          default=DeviceStatusChoices.STATUS_ACTIVE.value)

	class Meta:
		verbose_name = _("device")
		verbose_name_plural = _("devices")

	def __str__(self):
		return self.name

	def clean(self):
		# Validate manufacturer/platform
		if hasattr(self, 'device_type') and self.platform:
			if self.platform.manufacturer and self.platform.manufacturer != self.device_type.manufacturer:
				raise ValidationError({
					'platform': "The assigned platform is limited to {} device types, but this device's type belongs "
					            "to {}.".format(self.platform.manufacturer, self.device_type.manufacturer)
				})
