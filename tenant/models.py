from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from mptt.managers import TreeManager
from mptt.models import MPTTModel, TreeForeignKey
from slugify import slugify


# Create your models here.
class TenantGroup(MPTTModel):
	name = models.CharField(max_length=100, unique=True, verbose_name=_("name"))
	slug = models.SlugField(unique=True, verbose_name=_("slug"), null=True, blank=True)
	parent = TreeForeignKey(to="self", on_delete=models.CASCADE, related_name='children', blank=True, null=True,
	                        db_index=True, verbose_name=_("parent"))
	description = models.CharField(max_length=100, blank=True, verbose_name=_("description"))
	created_at = models.DateTimeField(default=timezone.now, verbose_name=_("created at"))
	objects = TreeManager()

	class Meta:
		verbose_name = _("tenant group")
		verbose_name_plural = _("tenant groups")
		ordering = ["name"]

	class MPTTMeta:
		order_insertion_by = ["name"]

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = self.create_slug(self.name, self.parent)
		self.full_clean()
		super(TenantGroup, self).save(*args, **kwargs)

	@staticmethod
	def create_slug(name, parent=None):
		slug = slugify(name)
		if parent:
			slug = "{parent_pk}-{slug}".format(parent_pk=parent.pk, slug=slug)
		return slug[:50]


class Tenant(models.Model):
	name = models.CharField(max_length=100, unique=True, verbose_name=_("name"))
	slug = models.SlugField(unique=True, verbose_name=_("slug"), null=True, blank=True)
	group = models.ForeignKey(to=TenantGroup, on_delete=models.SET_NULL, related_name="tenants", blank=True, null=True)
	description = models.CharField(max_length=200, blank=True, verbose_name=_("description"))
	created_at = models.DateTimeField(default=timezone.now, verbose_name=_("created at"))

	class Meta:
		verbose_name = _("tenant")
		verbose_name_plural = _("tenants")

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = self.create_slug(self.name, self.group)
		self.full_clean()
		super(Tenant, self).save(*args, **kwargs)

	@staticmethod
	def create_slug(name, parent=None):
		slug = slugify(name)
		if parent:
			slug = "{parent_pk}-{slug}".format(parent_pk=parent.pk, slug=slug)
		return slug[:50]
