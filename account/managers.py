from django.db import models


class EmailAddressManager(models.Manager):
	def get_users_for(self, email):
		for email_address in self.filter(verified=True, email=email):
			return email_address.user

	def add_email(self, user, email, confirm=False):
		email_address = self.create(user=user, email=email)
		if confirm and not email_address.verified:
			email_address.send_confirmation()
		return email_address

	def get_primary(self, user):
		try:
			return self.get(user=user, primary=True)
		except self.model.DoesNotExist:
			return None
