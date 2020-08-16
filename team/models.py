import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from slugify import slugify

from invite.models import JoinInvitation


# Create your models here.
class Team(models.Model):
	MEMBER_ACCESS_OPEN = "open"
	MEMBER_ACCESS_APPLICATION = "application"
	MEMBER_ACCESS_INVITATION = "invitation"

	MANAGER_ACCESS_ADD = "add someone"
	MANAGER_ACCESS_INVITE = "invite someone"

	MEMBER_ACCESS_CHOICES = [
		(MEMBER_ACCESS_OPEN, _("open")),
		(MEMBER_ACCESS_APPLICATION, _("by application")),
		(MEMBER_ACCESS_INVITATION, _("by invitation"))
	]

	MANAGER_ACCESS_CHOICES = [
		(MANAGER_ACCESS_ADD, _("add someone")),
		(MANAGER_ACCESS_INVITE, _("invite someone"))
	]

	name = models.CharField(max_length=200, verbose_name=_("name"))
	slug = models.SlugField(unique=True, verbose_name=_("slug"), null=True, blank=True)
	avatar = models.ImageField(upload_to="avatar", verbose_name=_("avatar"), blank=True, null=True)
	description = models.TextField(blank=True, null=True, verbose_name=_("description"))
	owner = models.ForeignKey(to=User, verbose_name=_("owner"), on_delete=models.CASCADE, related_name="owner")
	member_access = models.CharField(choices=MEMBER_ACCESS_CHOICES, max_length=20, verbose_name=_("member access"))
	manager_access = models.CharField(max_length=20, choices=MANAGER_ACCESS_CHOICES, verbose_name=_("manager access"))
	parent = models.ForeignKey(to="self", blank=True, null=True, related_name="children", on_delete=models.CASCADE)
	created_at = models.DateTimeField(default=timezone.now, verbose_name=_("created at"))

	class Meta:
		verbose_name = _("team")
		verbose_name_plural = _("teams")

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = self.create_slug(self.name, self.parent)
		self.full_clean()
		super(Team, self).save(*args, **kwargs)

	def clean(self):
		if self.pk and self.pk == self.parent_id:
			raise ValidationError({"parent": "A team cannot be a parent of itself"})

	@staticmethod
	def create_slug(name, parent=None):
		slug = slugify(name)
		if parent:
			slug = "{parent_pk}-{slug}".format(parent_pk=parent.pk, slug=slug)
		return slug[:50]

	def can_join(self, user):
		state = self.state_for(user)
		if self.member_access == Team.MEMBER_ACCESS_OPEN and state is None:
			return True
		elif self.member_access == Membership.STATE_INVITED:
			return True
		return False

	def can_leave(self, user):
		role = self.role_for(user)
		return role == Membership.ROLE_MEMBER

	def can_apply(self, user):
		state = self.state_for(user)
		return self.member_access == Team.MEMBER_ACCESS_APPLICATION and state is None

	def get_parent_team(self):
		team = self
		while getattr(team, "parent"):
			team = team.parent
		return team

	@property
	def ancestors(self):
		team = self
		chain = []
		while getattr(team, "parent"):
			chain.append(team)
			team = team.parent
		chain.append(team)
		chain.reverse()
		return chain

	@property
	def descendants(self):
		_descendants = []
		for child in self.children.all():
			_descendants.append(child.descendants)
		return _descendants

	@property
	def full_name(self):
		return " : ".join([a.name for a in self.ancestors])

	@property
	def applicants(self):
		return self.memberships.filter(state=Membership.STATE_APPLIED)

	@property
	def invitees(self):
		return self.memberships.filter(state=Membership.STATE_INVITED)

	@property
	def declines(self):
		return self.memberships.filter(state=Membership.STATE_DECLINED)

	@property
	def rejections(self):
		return self.memberships.filter(state=Membership.STATE_REJECTED)

	@property
	def waitlisted(self):
		return self.memberships.filter(state=Membership.STATE_WAITLISTED)

	@property
	def acceptances(self):
		return self.memberships.filter(state__in=[
			Membership.STATE_ACCEPTED,
			Membership.STATE_AUTO_JOINED]
		)

	@property
	def members(self):
		return self.acceptances.filter(role=Membership.ROLE_MEMBER)

	@property
	def managers(self):
		return self.acceptances.filter(role=Membership.ROLE_MANAGER)

	@property
	def owners(self):
		return self.acceptances.filter(role=Membership.ROLE_OWNER)

	def is_owner_or_manager(self, user):
		return self.acceptances.filter(
			role__in=[
				Membership.ROLE_OWNER,
				Membership.ROLE_MANAGER
			],
			user=user
		).exists()

	def is_member(self, user):
		return self.members.filter(user=user).exists()

	def is_manager(self, user):
		return self.managers.filter(user=user).exists()

	def is_owner(self, user):
		return self.owners.filter(user=user).exists()

	def is_on_team(self, user):
		return self.acceptances.filter(user=user).exists()

	def add_member(self, user, role=None, state=None, by=None):
		if role is None:
			role = Membership.ROLE_MEMBER
		if state is None:
			state = Membership.STATE_AUTO_JOINED

		membership, _ = self.memberships.get_or_create(team=self, user=user, defaults={"role": role, "state": state})
		return membership

	def add_user(self, user, role, by=None):
		state = Membership.STATE_AUTO_JOINED
		if self.manager_access == Team.MANAGER_ACCESS_INVITE:
			state = Membership.STATE_INVITED
		membership, _ = self.memberships.get_or_create(user=user, defaults={"role": role, "state": state})
		return membership

	def invite_user(self, from_user, to_email, role, message=None):
		if not JoinInvitation.objects.filter(invite_code__email=to_email).exists():
			invite = JoinInvitation.invite(from_user=from_user, to_email=to_email, message=message, send=False)
			membership, _ = self.memberships.get_or_create(invite=invite,
			                                               defaults={"role": role, "state": Membership.STATE_INVITED})
			invite.send_invite()
			return membership

	def for_user(self, user):
		attr = "_membership_for_user"
		if hasattr(self, attr) is False:
			team = self
			membership = None
			while team:
				try:
					membership = team.memberships.get(user=user)
					break
				except ObjectDoesNotExist:
					team = team.parent
			setattr(self, attr, membership)
		return getattr(self, attr)

	def state_for(self, user):
		membership = self.for_user(user)
		if membership:
			return membership.state

	def role_for(self, user):
		if getattr(user, "is_staff", False):
			return Membership.ROLE_MANAGER
		membership = self.for_user(user)
		if membership:
			return membership.role


class Membership(models.Model):
	STATE_APPLIED = "applied"
	STATE_INVITED = "invited"
	STATE_DECLINED = "declined"
	STATE_REJECTED = "rejected"
	STATE_ACCEPTED = "accepted"
	STATE_WAITLISTED = "waitlisted"
	STATE_AUTO_JOINED = "auto-joined"

	ROLE_MEMBER = "member"
	ROLE_MANAGER = "manager"
	ROLE_OWNER = "owner"

	STATE_CHOICES = [
		(STATE_APPLIED, _("applied")),
		(STATE_INVITED, _("invited")),
		(STATE_DECLINED, _("declined")),
		(STATE_REJECTED, _("rejected")),
		(STATE_ACCEPTED, _("accepted")),
		(STATE_WAITLISTED, _("waitlisted")),
		(STATE_AUTO_JOINED, _("auto joined"))
	]

	ROLE_CHOICES = [
		(ROLE_MEMBER, _("member")),
		(ROLE_MANAGER, _("manager")),
		(ROLE_OWNER, _("owner"))
	]

	team = models.ForeignKey(Team, related_name="memberships", verbose_name=_("team"), on_delete=models.CASCADE)
	user = models.ForeignKey(to=User, related_name="memberships", null=True, blank=True, verbose_name=_("user"),
	                         on_delete=models.CASCADE)
	invite = models.ForeignKey(to=JoinInvitation, related_name="memberships", null=True, blank=True,
	                           verbose_name=_("invite"), on_delete=models.CASCADE)
	state = models.CharField(max_length=20, choices=STATE_CHOICES, verbose_name=_("state"))
	role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name=_("role"))
	created_at = models.DateTimeField(default=timezone.now, verbose_name=_("created at"))

	class Meta:
		verbose_name = _("membership")
		verbose_name_plural = _("memberships")
		unique_together = [("team", "user", "invite")]

	def __str__(self):
		return "{0} in {1}".format(self.user, self.team)

	def is_owner(self):
		return self.role == Membership.ROLE_OWNER

	def is_manager(self):
		return self.role == Membership.ROLE_MANAGER

	def is_member(self):
		return self.role == Membership.ROLE_MEMBER

	def promote(self, by):
		role = self.team.role_for(by)
		if role in [Membership.ROLE_MANAGER, Membership.ROLE_OWNER]:
			if self.role == Membership.ROLE_MEMBER:
				self.role = Membership.ROLE_MANAGER
				self.save()
				return True
		return False

	def demote(self, by):
		role = self.team.role_for(by)
		if role in [Membership.ROLE_MANAGER, Membership.ROLE_OWNER]:
			if self.role == Membership.ROLE_MANAGER:
				self.role = Membership.ROLE_MEMBER
				self.save()
				return True
		return False

	def accept(self, by):
		role = self.team.role_for(by)
		if role in [Membership.ROLE_MANAGER, Membership.ROLE_OWNER]:
			if self.state == Membership.STATE_APPLIED:
				self.state = Membership.STATE_ACCEPTED
				self.save()
				return True
		return False

	def reject(self, by):
		role = self.team.role_for(by)
		if role in [Membership.ROLE_MANAGER, Membership.ROLE_OWNER]:
			if self.state == Membership.STATE_APPLIED:
				self.state = Membership.STATE_REJECTED
				self.save()
				return True
		return False

	def joined(self):
		self.user = self.invite.to_user
		if self.team.manager_access == Team.MANAGER_ACCESS_ADD:
			self.state = Membership.STATE_AUTO_JOINED
		else:
			self.state = Membership.STATE_INVITED
		self.save()

	def status(self):
		if self.user:
			return self.get_state_display()
		if self.invite:
			return self.invite.get_status_display()
		return "Unknown"

	def resend_invite(self, by=None):
		if self.invite is not None:
			code = self.invite.signup_code
			code.expiry = timezone.now() + datetime.timedelta(days=5)
			code.save()
			code.send()

	def remove(self, by=None):
		if self.invite is not None:
			self.invite.signup_code.delete()
			self.invite.delete()
		self.delete()

	@property
	def invitee(self):
		return self.user or self.invite.to_user_email()
