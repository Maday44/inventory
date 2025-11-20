from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from .models import Food_items, Other_items, Profile
from django.contrib.auth import logout
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from .forms import *
from django.urls import reverse
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone

@login_required
@permission_required('storage.add_fooditems', raise_exception=True)
def add_food(request):
    if request.method == "POST":
        form = FoodForm(request.POST, request.FILES)
        if form.is_valid():
            food = form.save(commit=False)
            food.family = request.user.profile.family 
            food.save()
            return redirect("all_food") 
    else:
        form = FoodForm()

    return render(request, "storage/add_food.html", {"form": form})

@login_required
@permission_required('storage.add_otheritems', raise_exception=True)
def add_other_items(request):
    if request.method == "POST":
        form = OtherForm(request.POST, request.FILES)
        if form.is_valid():
            other = form.save(commit=False)
            other.family = request.user.profile.family  # assign user's family
            other.save()
            return redirect("all_other_items")  # redirect to food list
    else:
        form = OtherForm()

    # Render a dedicated 'add food' template (not food_detail)
    return render(request, "storage/add_other.html", {"form": form})


@login_required
# home page: show all items in the user's family
def view_all_items(request):
    user_family = request.user.profile.family
    food_items = Food_items.objects.filter(family=user_family,is_active=True,exp_date__gte=timezone.now().date()).order_by('exp_date')
    other_items = Other_items.objects.filter(family=user_family)
    return render(request, 'storage/home.html', {'foods': food_items, 'others': other_items})


@login_required
# see all the food in user's family
def all_food(request):
    user_family = request.user.profile.family
    food_items = Food_items.objects.filter(
        family=user_family,
        is_active=True
    ).order_by('exp_date')
    return render(request, 'storage/allFoodPage.html', {'foods': food_items})




@login_required
# see all other items in user's family
def all_other(request):
    user_family = request.user.profile.family
    other_items = Other_items.objects.filter(family=user_family)
    return render(request, 'storage/allOtherPage.html', {'Others': other_items})

@login_required
def food_detail(request, slug):
    # Only show item if it belongs to user's family
    food = get_object_or_404(Food_items, slug=slug, family=request.user.profile.family)
    return render(request, "storage/food_detail.html", {"food": food})

@login_required
def other_detail(request, slug):
    # Only show item if it belongs to user's family
    other = get_object_or_404(Other_items, slug=slug, family=request.user.profile.family)
    return render(request, "storage/other_detail.html", {"other": other})


def choose_add_food(request):
    return render(request, "storage/choose_add_food.html")

def choose_add_other(request):
    return render(request, "storage/choose_add_other.html")

@login_required
def profile_detail(request, user_id=None):
    """
    Show a user's profile:
    - Owners can view all profiles
    - Admins can view only users in their family
    - Regular users can view only themselves
    """
    current_user_profile = request.user.profile

    if user_id is None:
        profile = current_user_profile
    else:
        profile = get_object_or_404(Profile, user__id=user_id)

        if current_user_profile.role == Profile.Role.OWNER:
            pass
        elif current_user_profile.role == Profile.Role.ADMIN:
            if profile.family != current_user_profile.family:
                return render(request, "403.html", status=403)
        else:
            if profile.user != request.user:
                return render(request, "403.html", status=403)

    return render(request, "storage/profile.html", {"profile": profile})


@login_required
def edit_profile(request, id):
    profile = get_object_or_404(Profile, id=id)

    if request.user != profile.user and request.user.profile.role != Profile.Role.OWNER:
        return redirect('profile_detail', id=request.user.id)

    if request.method == "POST":
        profile.display_name = request.POST.get("display_name")
        if request.FILES.get("profile_pic"):
            profile.profile_pic = request.FILES["profile_pic"]
        if request.user.profile.role == Profile.Role.OWNER and request.POST.get("role"):
            profile.role = request.POST.get("role")
        profile.save()
        return redirect('profile_detail', id=profile.id)

    return render(request, "storage/edit_profile.html", {"profile": profile})


def custom_logout(request):
    if request.method == 'POST':
        logout(request)
        return render(request, 'logout_thanks.html')  # thank-you page
    else:
        return redirect('/')  # redirect GET requests away

@login_required
def food_item_delete(request, slug):
    food = get_object_or_404(Food_items, slug=slug)
    if request.user.profile.role != Profile.Role.OWNER and Profile.Role.ADMIN:
        return HttpResponseForbidden("Access Denied")

    if request.method == "POST":
        food.delete()
        return redirect(f"{reverse('all_food')}?success=1")

    return render(request, "storage/confirm_delete.html", {"food": food})

@login_required
def other_item_delete(request, slug):
    other = get_object_or_404(Other_items, slug=slug)
    if request.user.profile.role != Profile.Role.OWNER and Profile.Role.ADMIN:
        return HttpResponseForbidden("Access Denied")

    if request.method == "POST":
        other.delete()
        return redirect(f"{reverse('all_other_items')}?success=1")

    return render(request, "storage/confirm_delete.html", {"other": other})


@login_required
@permission_required('storage.change_fooditems', raise_exception=True)
def food_edit(request, slug):
    food = get_object_or_404(Food_items, slug=slug)
    
    if request.user.profile.role != Profile.Role.OWNER and Profile.Role.ADMIN:
        return HttpResponseForbidden("Access Denied")

    if request.method == "POST":
        form = FoodForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('food-detail', args=[food.slug])}?success=1")
    else:
        form = FoodForm(instance=food)

    return render(request, "storage/add_food.html", {
        "form": form,
        "food": food, 
        "is_edit": True  
    })

@login_required
@permission_required('storage.change_otheritems', raise_exception=True)
def other_edit(request, slug):
    other = get_object_or_404(Other_items, slug=slug)
    
    if request.user.profile.role != Profile.Role.OWNER and Profile.Role.ADMIN:
        return HttpResponseForbidden("Access Denied")

    if request.method == "POST":
        form = OtherForm(request.POST, request.FILES, instance=other)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('other-detail', args=[other.slug])}?success=1")
    else:
        form = OtherForm(instance=other)

    return render(request, "storage/add_other.html", {
        "form": form,
        "other": other, 
        "is_edit": True  
    })


    
def all_members(request):
    family = request.user.profile.family 
    members = family.members.select_related("user").all() 
    return render(request, "storage/members.html", {"family": family, "members": members})

def member_detail(request):
    pass


@login_required
def edit_member_view(request, member_id):
    member = get_object_or_404(Profile, id=member_id, family=request.user.profile.family)

    if request.method == "POST":
        new_role = request.POST.get("role")
        if request.user.profile.role in ["owner", "admin"]:  # only admins/owners can edit
            member.role = new_role
            member.save()
        return redirect("family_members")

    return render(request, "storage/edit_member.html", {"member": member})

@login_required
def category_list(request):
    family = request.user.profile.family
    categories = Category.objects.filter(Q(is_default=True) | Q(family=family))

    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            # Check if category already exists for this family
            if not Category.objects.filter(name=name, family=family).exists():
                Category.objects.create(name=name, family=family, is_default=False)
            return redirect("category")
    else:
        form = CategoryForm()

    context = {
        "categories": categories,
        "form": form,
    }
    return render(request, "storage/category.html", context)

def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk, family=request.user.profile.family)
    if category.is_default:
        messages.error(request, "Default categories cannot be deleted.")
    else:
        category.delete()
        messages.success(request, f"Category '{category.name}' deleted successfully.")
    return redirect("category")

def manage_expiry(request, item_id):
    item = get_object_or_404(Food_items, id=item_id, family=request.user.profile.family)
    expiry = item.expiry_records.filter(is_active=True).first()
    
    if request.method == "POST":
        form = ItemExpiryForm(request.POST, instance=expiry)
        if form.is_valid():
            expiry = form.save(commit=False)
            expiry.item = item
            expiry.is_active = True
            expiry.save()
            messages.success(request, "Expiry date updated successfully!")
            return redirect("manage_expiry", item_id=item.id)
    else:
        form = ItemExpiryForm(instance=expiry)

    return render(request, "storgae/manage_expiry.html", {"item": item, "form": form, "expiry": expiry})

def delete_expiry(request, pk):
    expiry = get_object_or_404(ItemExpiry, pk=pk, item__family=request.user.profile.family)
    expiry.is_active = False
    expiry.save()
    messages.success(request, "Expiry tracking removed for this item.")
    return redirect("manage_expiry", item_id=expiry.item.id)


def delete_item(request, pk):
    item = get_object_or_404(Food_items, pk=pk, family=request.user.profile.family)
    item.is_active = False
    item.deleted_on = timezone.now()
    item.delete()
    messages.info(request, f"{item.title} has now been deleted")
    return redirect("all_food")


def restore_item(request, pk):
    item = get_object_or_404(Food_items, pk=pk, family=request.user.profile.family, is_active=False)
    item.is_active = True
    item.deleted_on = None
    item.restored = True
    item.save()
    messages.success(request, f"{item.title} restored successfully.")
    return redirect("all_food")


def expired_items(request):
    user_family = request.user.profile.family
    today = timezone.now().date()

    expired_foods = Food_items.objects.filter(
        family=user_family,
        exp_date__lt=today,
        is_active=False  
    ).order_by('exp_date')

    return render(request, "storage/expired_items.html", {"foods": expired_foods})

#shop add 