from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


admin.site.register(Food_items)
admin.site.register(Other_items)
admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Shopitems)
admin.site.register(ShoppingList)



class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 1

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)




@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ("name", "member_count", "get_members")
    inlines = [ProfileInline]

    def member_count(self, obj):
        return obj.members.count()

    member_count.short_description = "Number of Members"

    def get_members(self, obj):
        members = obj.members.all()
        if members.exists():
            return ", ".join([m.display_name for m in members])
        return "No members"

    get_members.short_description = "Members"
