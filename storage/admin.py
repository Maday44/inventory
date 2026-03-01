from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import *

admin.site.register(Food_items)
admin.site.register(Other_items)
admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Shopitems)
admin.site.register(ShoppingList)
admin.site.register(Family)
admin.site.register(FamilyMember)
admin.site.register(Recipe)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "user")
    search_fields = ("display_name", "user__username")


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0


class FamilyMemberInline(admin.TabularInline):
    model = FamilyMember
    extra = 1
    autocomplete_fields = ["profile"]


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class FamilyAdmin(admin.ModelAdmin):
    list_display = ("name", "member_count", "get_members")
    inlines = [FamilyMemberInline]

    def member_count(self, obj):
        return obj.memberships.count()

    member_count.short_description = "Number of Members"

    def get_members(self, obj):
        members = obj.memberships.select_related("profile")
        if members.exists():
            return ", ".join([m.profile.display_name for m in members])
        return "No members"

    get_members.short_description = "Members"
