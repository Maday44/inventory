from django.contrib import admin
from .models import Food_items, Other_items, Family, Profile,Category

admin.site.register(Food_items)
admin.site.register(Other_items)
admin.site.register(Profile)
admin.site.register(Category)

class ProfileInline(admin.TabularInline):
    model = Profile
    extra = 0
    fields = ("display_name", "role", "user")

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
