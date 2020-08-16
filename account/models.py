from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from djmoney.models.fields import MoneyField
from account.managers import EmailAddressManager
from django.utils import timezone
from datetime import timedelta
import secrets
from account import signals
from django.core.mail import send_mail
from django.template.loader import render_to_string


# Create your models here.

class Account(models.Model):
	user = models.OneToOneField(to=User, on_delete=models.CASCADE, verbose_name=_("user"))
	avatar = models.ImageField(upload_to="avatar", verbose_name=_("avatar"), blank=True, null=True)
	balance = MoneyField(max_digits=19, decimal_places=4, default=0, default_currency="USD", verbose_name=_("balance"))
	credit = MoneyField(max_digits=19, decimal_places=4, default=0, default_currency="USD", verbose_name=_("credit"))

	class Meta:
		verbose_name = _("account")
		verbose_name_plural = _("accounts")
		ordering = ["-user"]

	def __str__(self):
		return self.user


class EmailAddress(models.Model):
	user = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name=_("user"))
	email = models.EmailField(max_length=254, unique=True)
	verified = models.BooleanField(default=False, verbose_name=_("verified"))
	primary = models.BooleanField(default=False, verbose_name=_("primary"))

	object = EmailAddressManager()

	class Meta:
		verbose_name = _("email address")
		verbose_name_plural = _("email addresses")

	def __str__(self):
		return "{0}:{1}".format(self.email, self.user)

	def set_primary(self):
		old_primary = EmailAddress.object.get(self.user)
		if old_primary:
			old_primary.primary = False
			old_primary.save()
		self.primary = True
		self.save()
		self.user.email = self.email
		self.user.save()
		return True

	def send_confirmation(self):
		confirmation = EmailAddressConfirmation.create(self.email)
		confirmation.send()
		return confirmation

	def change(self, new_email, confirm=True):
		with transaction.atomic():
			self.user.email = new_email
			self.user.save()
			self.email = new_email
			self.verified = False
			self.save()
			if confirm:
				self.send_confirmation()


class EmailAddressConfirmation(models.Model):
	email = models.ForeignKey(to=EmailAddress, on_delete=models.CASCADE, verbose_name=_("email"))
	created_at = models.DateTimeField(default=timezone.now, verbose_name=_("created at"))
	sent_at = models.DateTimeField(null=True, verbose_name=_("sent_at"))
	token = models.CharField(max_length=64, unique=True, verbose_name=_("token"))

	# token_expired = models.BooleanField(default=False, verbose_name=_("token expired"))

	class Meta:
		verbose_name = _("email address confirmation")
		verbose_name_plural = _("email address confirmations")

	def __str__(self):
		return self.email

	@classmethod
	def create(cls, email):
		return cls.objects.create(email=email, token=secrets.token_urlsafe(32))

	def token_expired(self):
		expiration_date = self.sent_at + timedelta(settings.ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS)
		return expiration_date <= timezone.now()

	def confirm(self):
		if not self.token_expired() and not self.email.verified:
			email = self.email
			email.verified = True
			email.set_primary()
			email.save()
			signals.email_confirmed.send(sender=self.__class__, email=email)
			return email

	def send(self):
		# TODO: update activate url
		activate_url = ""
		context = {
			"activate_url": activate_url,
			"email": self.email,
			"user": self.email.user,
			"token": self.token
		}
		self.send_confirmation_email(to=self.email, context=context)
		self.sent_at = timezone.now()
		self.save()
		signals.email_confirmation_sent.send(sender=self.__class__, confirmation=self)

	def send_confirmation_email(self, to, context):
