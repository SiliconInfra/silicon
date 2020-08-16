import datetime
import functools
import operator
import secrets

from django.conf import settings
from django.contrib.auth.models import User, User, User
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from eventlog.utils import EmailMessage


# Create your models here.
class InviteCode(models.Model):
	code = models.CharField(max_length=64, unique=True, verbose_name=_("code"), default=secrets.token_urlsafe(8))
	expiry = models.DateTimeField(null=True, blank=True, verbose_name=_("expiry"))
	invite_from = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name=_("invite from"))
	email = models.EmailField(verbose_name=_("email"))
	created_at = models.DateTimeField(default=timezone.now, verbose_name=_("created at"))
	sent_at = models.DateTimeField(null=True, blank=True, verbose_name=_("sent at"))

	class Meta:
		verbose_name = _("invite code")
		verbose_name_plural = _("invite codes")

	def __str__(self):
		return "{0} [{1}]".format(self.email, self.code)

	@classmethod
	def exists(cls, code=None, email=None):
		checks = []
		if code:
			checks.append(Q(code=code))
		if email:
			checks.append(Q(email=email))
		if not checks:
			return False
		return cls.objects.filter(functools.reduce(operator.or_, checks)).exists()

	@classmethod
	def create(cls, email, from_user, code=None):
		if cls.exists(code=code, email=email):
			raise Exception("Invite code for %s already exists", email)
		expiry = timezone.now() + datetime.timedelta(hours=24)
		if not code:
			code = cls.generate_invite_code()
		context = {
			"code": code,
			"email": email,
			"expiry": expiry,
			"invite_from": from_user
		}

		return cls(**context)

	@classmethod
	def check_code(cls, code):
		try:
			invite_code = cls.objects.get(code=code)
		except cls.DoesNotExist:
			raise Exception("Invite code does not exist")
		else:
			if invite_code.expiry and timezone.now() > invite_code.expiry:
				raise Exception("Invite code has expired")
			return invite_code

	def send(self):
		# TODO: Add invite code URL
		invite_url = ""
		context = {
			"invite_url": invite_url,
			"code": self.code
		}
		self.send_invite_email(self.email, context)
		self.sent_at = timezone.now()
		self.save()

	@staticmethod
	def generate_invite_code():
		return secrets.token_urlsafe(8)

	@staticmethod
	def send_invite_email(email, context):
		EmailMessage().send(
			subject_template="account/email/email_confirmation_subject.html", subject_context=context,
			message_template="account/email/email_confirmation_message.html", message_context=context,
			from_email=settings.DEFAULT_FROM_EMAIL, to=email)


class JoinInvitation(models.Model):
	STATUS_SENT = 1
	STATUS_ACCEPTED = 2

	INVITE_STATUS_CHOICES = [
		(STATUS_SENT, "Sent"),
		(STATUS_ACCEPTED, "Accepted")
	]

	from_user = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name=_("from user"),
	                              related_name="invite_sent")
	to_user = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name=_("to user"),
	                            related_name="invite_received", null=True, blank=True)
	message = models.TextField(null=True, blank=True, verbose_name=_("message"))
	invite_code = models.OneToOneField(to=InviteCode, on_delete=models.CASCADE, verbose_name=_("invite code"))
	status = models.IntegerField(choices=INVITE_STATUS_CHOICES, verbose_name=_("status"))
	sent_at = models.DateTimeField(default=timezone.now, verbose_name=_("sent at"))

	class Meta:
		verbose_name = _("join invitation")
		verbose_name_plural = _("join invitations")

	def __str__(self):
		return "{0} -> {1}".format(self.from_user, self.to_user)

	def to_user_email(self):
		return self.invite_code.email

	def accept(self, user):
		self.to_user = user
		self.status = JoinInvitation.STATUS_ACCEPTED
		self.save()

	@classmethod
	def invite(cls, from_user, to_email, message=None, send=True):
		invite_code = InviteCode.create(email=to_email, from_user=from_user)
		invite_code.save()
		join = cls.objects.create(from_user=from_user, message=message, status=JoinInvitation.STATUS_SENT,
		                          invite_code=invite_code)

		invite_code.send()
		return join
