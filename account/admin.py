from django.contrib import admin
from account.models import Account, EmailAddress, EmailAddressConfirmation


# Register your models here.
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
	raw_id_fields = ["user"]
	list_display = ["user", "balance", "credit"]
	search_fields = ["user__username", "user__email"]


@admin.register(EmailAddress)
class EmailAddressAdmin(admin.ModelAdmin):
	list_display = ["user", "email", "verified", "primary"]
	search_fields = ["email", "user__username"]


@admin.register(EmailAddressConfirmation)
class EmailAddressConfirmationAdmin(admin.ModelAdmin):
	readonly_fields = ["token"]
	list_display = ["email", "created_at", "sent_at", "token"]
	search_fields = ["email"]
	list_filter = ["created_at", "sent_at"]
