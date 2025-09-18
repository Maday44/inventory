
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect
from .models import Food_items, Other_items

@login_required
@permission_required('storage.add_fooditems', raise_exception=True)
def add_food_item(request):
    # Only admins can access this view
    return render(request,"food_detail.jsx")

@login_required
@permission_required('storage.change_fooditems', raise_exception=True)
def edit_item_quantity(request, item_id):
    # Both user and admin can edit
    pass

@login_required
# home page
def view_all_items(request):
    food_items = Food_items.objects.all().order_by('exp_date')
    other_items = Other_items.objects.all()
    return render(request, 'home.jsx', {'foods': food_items, 'others': other_items})

@login_required
# home page
def all_food(request):
    food_items = Food_items.objects.all().order_by('exp_date')
    return render(request, 'all_food.jsx', {'foods': food_items})

def home(request):
    pass