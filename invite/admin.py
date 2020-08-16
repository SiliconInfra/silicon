from django.contrib import admin

from invite.models import InviteCode, JoinInvitation


# Register your models here.
@admin.register(InviteCode)
class InviteCodeAdmin(admin.ModelAdmin):
	readonly_fields = ["code"]
	list_display = ["invite_from", "email", "code", "expiry", "created_at", "sent_at"]
	list_filter = ["created_at", "sent_at"]
	search_fields = ["invite_from__username", "invite_from__email"]


@admin.register(JoinInvitation)
class JoinInvitationAdmin(admin.ModelAdmin):
	list_display = ["from_user", "to_user", "invite_code", "status", "sent_at"]
	list_filter = ["from_user", "to_user", "sent_at"]
	search_fields = ["from_user__username", "from_user__email", "to_user__username", "to_user__email"]
