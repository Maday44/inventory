from django.contrib import admin
from .models import Food_items, Other_items, User, Family

admin.site.register(Food_items)
admin.site.register(Other_items)
admin.site.register(User)
admin.site.register(Family)

