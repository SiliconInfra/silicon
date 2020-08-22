from django.contrib import admin

from invite.models import InviteCode, JoinInvitation


# Register your models here.
@admin.register(InviteCode)
class InviteCodeAdmin(admin.ModelAdmin):
	readonly_fields = ["code", "expiry", "created_at", "sent_at"]
	list_display = ["invite_from", "email", "code", "expiry", "created_at", "sent_at"]
	list_filter = ["created_at", "sent_at"]
	search_fields = ["invite_from__username", "invite_from__email"]

	def save_model(self, request, obj, form, change):
		invite_code = obj.create(email=obj.email, from_user=obj.invite_from)
		invite_code.save()


@admin.register(JoinInvitation)
class JoinInvitationAdmin(admin.ModelAdmin):
	readonly_fields = ["sent_at"]
	list_display = ["from_user", "to_user", "invite_code", "status", "sent_at"]
	list_filter = ["from_user", "to_user", "sent_at"]
	search_fields = ["from_user__username", "from_user__email", "to_user__username", "to_user__email"]
