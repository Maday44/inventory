
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect
from .models import Food_items, Other_items

@login_required
@permission_required('storage.add_fooditems', raise_exception=True)
def add_food_item(request):
    # Only admins can access this view
    pass

@login_required
@permission_required('storage.change_fooditems', raise_exception=True)
def edit_item_quantity(request, item_id):
    # Both user and admin can edit
    pass

@login_required
def view_all_items(request):
    food_items = Food_items.objects.all()
    other_items = Other_items.objects.all()
    return render(request, 'view_items.jsx', {'foods': food_items, 'others': other_items})
