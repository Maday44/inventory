from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from .models import Food_items, Other_items, Profile
from django.contrib.auth import logout

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from .forms import *  # make sure this exists

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
@permission_required('storage.change_fooditems', raise_exception=True)
def edit_item_quantity(request, item_id):
    # Both user and admin can edit, only within their family
    food = get_object_or_404(Food_items, id=item_id, family=request.user.profile.family)

    if request.method == "POST":
        food.quantity = request.POST.get("quantity", food.quantity)
        food.save()
        return redirect("all_food")

    return render(request, "storage/edit_food.html", {"food": food})


@login_required
# home page: show all items in the user's family
def view_all_items(request):
    user_family = request.user.profile.family
    food_items = Food_items.objects.filter(family=user_family).order_by('exp_date')
    other_items = Other_items.objects.filter(family=user_family)
    return render(request, 'storage/home.html', {'foods': food_items, 'others': other_items})


@login_required
# see all the food in user's family
def all_food(request):
    user_family = request.user.profile.family
    food_items = Food_items.objects.filter(family=user_family).order_by('exp_date')
    return render(request, 'storage/allFoodPage.html', {'foods': food_items})


@login_required
# see all other items in user's family
def all_other(request):
    user_family = request.user.profile.family
    other_items = Other_items.objects.filter(family=user_family)
    return render(request, 'storage/allOtherPage.html', {'Others': other_items})


def food_detail(request, slug):
    # Only show item if it belongs to user's family
    food = get_object_or_404(Food_items, slug=slug, family=request.user.profile.family)
    return render(request, "storage/food_detail.html", {"food": food})


def other_detail(request, slug):
    # Only show item if it belongs to user's family
    other = get_object_or_404(Other_items, slug=slug, family=request.user.profile.family)
    return render(request, "storage/other_detail.html", {"other": other})


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

'''
@login_required
def album_delete(request, id):
    album = get_object_or_404(Album, id=id)
    profile = request.user.profile
    if profile.role != MusicManagerUser.Role.EDITOR:
        return HttpResponseForbidden("Access Denied")

    if request.method == "POST":
        album.delete()
        return redirect(f"{reverse('album-list')}?success=1")

    return render(request, "label_music_manager/album_confirm_delete.html", {"album": album})


@login_required
def album_create(request):
    profile = request.user.profile
    
    if profile.role != MusicManagerUser.Role.EDITOR:
        return HttpResponseForbidden("Access Denied")

    if request.method == "POST":
        form = AlbumForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        form = AlbumForm()

    return render(request, "label_music_manager/album_form.html", {"form": form})

@login_required
@permission_required('label_music_manager.change_album', raise_exception=True)
def album_edit(request, id):
    album = get_object_or_404(Album, id=id)
    profile = request.user.profile
    
    if profile.role != MusicManagerUser.Role.EDITOR and album.artist != profile.display_name:
        return HttpResponseForbidden("Access Denied")

    if request.method == "POST":
        form = AlbumForm(request.POST, request.FILES, instance=album)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('album-detail', args=[album.id])}?success=1")
    else:
        form = AlbumForm(instance=album)

    return render(request, "label_music_manager/album_form.html", {
        "form": form,
        "album": album, 
        "is_edit": True  
    })



'''