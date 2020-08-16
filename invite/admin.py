from django.contrib import admin
from invite.models import InviteCode


# Register your models here.
@admin.register(InviteCode)
class InviteCodeAdmin(admin.ModelAdmin):
	readonly_fields = ["code"]
	list_display = ["invite_from", "email", "code", "expiry", "created_at", "sent_at"]
	list_filter = ["created_at", "sent_at"]
	search_fields = ["invite_from__username", "invite_from__email"]
