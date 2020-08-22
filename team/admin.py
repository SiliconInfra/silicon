from django.contrib import admin

from team.models import Membership, Team


# Register your models here.
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
	readonly_fields = ["slug"]
	list_display = ["name", "slug", "parent", "tenant", "owner", "member_access", "manager_access", "created_at"]
	list_filter = ["created_at"]
	search_fields = ["name", "owner__username", "owner__email"]


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
	readonly_fields = ["created_at"]
	list_display = ["user", "team", "invite", "state", "role", "created_at"]
	list_filter = ["created_at", "role", "state"]
	search_fields = ["team__name", "user__username", "user__email"]
