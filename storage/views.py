
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect
from .models import Food_items, Other_items, Profile
from django.shortcuts import get_object_or_404, redirect

@login_required
@permission_required('storage.add_fooditems', raise_exception=True)
def add_food_item(request):
    # Only admins can access this view
    return render(request,"storage/food_detail.html")

@login_required
@permission_required('storage.change_fooditems', raise_exception=True)
def edit_item_quantity(request, item_id):
    # Both user and admin can edit
    return render(request,"storage/edit_food.html")

@login_required
# home page
def view_all_items(request):
    food_items = Food_items.objects.all().order_by('exp_date')
    other_items = Other_items.objects.all()
    return render(request, 'storage/home.html', {'foods': food_items, 'others': other_items})


@login_required
# see all the food
def all_food(request):
    food_items = Food_items.objects.all().order_by('exp_date')
    return render(request, 'storage/allFoodPage.html',{'foods': food_items})


def all_other(request):
    other_items = Other_items.objects.all()
    return render(request, 'storage/allOtherPage.html',{'Others': other_items})


def food_detail(request, id):
    food = get_object_or_404(Food_items, id=id)
    return render(request, "storage/food_detail.html", {"food": food})

def other_detail(request, id):
    other = get_object_or_404(Other_items, id=id)
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
        # If no user_id is provided, show the current user's profile
        profile = current_user_profile
    else:
        profile = get_object_or_404(Profile, user__id=user_id)

        # Role-based access control
        if current_user_profile.role == Profile.Role.OWNER:
            pass  # Owner can view anyone
        elif current_user_profile.role == Profile.Role.ADMIN:
            if profile.family != current_user_profile.family:
                return render(request, "403.html", status=403)
        else:  # USER
            if profile.user != request.user:
                return render(request, "403.html", status=403)

    return render(request, "storage/profile.html", {"profile": profile})

@login_required
def edit_profile(request, id):
    profile = get_object_or_404(Profile, id=id)

    # Only allow user to edit their own profile or owner/admin
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