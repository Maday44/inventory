from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Food_items, Other_items, Profile
from django.contrib.auth import logout, update_session_auth_hash
from authlib.integrations.django_client import OAuth
from django.contrib.auth.decorators import login_required, permission_required
from .forms import *
from django.urls import reverse
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from urllib.parse import quote_plus, urlencode
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
import requests
from django.core.files.base import ContentFile
from django.contrib.auth import login as django_login
import os

oauth = OAuth()

oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)


def login(request):
    return oauth.auth0.authorize_redirect(
        request,
        request.build_absolute_uri(reverse("callback"))
    )


def callback(request):
    try:
        token = oauth.auth0.authorize_access_token(request)
        userinfo = token["userinfo"]

        email = userinfo.get("email")
        if not email:
            return redirect(reverse("no_account"))

        email = email.lower()

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return redirect(reverse("no_account"))

        django_login(request, user)  
        request.session["user"] = userinfo 

        return redirect(reverse("view_all_items"))

    except Exception as e:
        print("CALLBACK ERROR:", e)
        return redirect(reverse("no_account"))


def logout(request):
    request.session.clear()

    auth0_logout_url = (
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("view_all_items")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        )
    )
    return render(request, "registration/logged_out.html", {"auth0_logout_url": auth0_logout_url})


def no_account(request):
    return render(request, "storage/no_account.html")

# change
@login_required
def custom_logout(request):
    if request.method == "POST":
        logout(request)
        return render(request, "logout_thanks.html") 
    else:
        return redirect("/")  


@login_required
@permission_required("storage.add_fooditems", raise_exception=True)
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
@permission_required("storage.add_otheritems", raise_exception=True)
def add_other_items(request):
    if request.method == "POST":
        form = OtherForm(request.POST, request.FILES)
        if form.is_valid():
            other = form.save(commit=False)
            other.family = request.user.profile.family 
            other.save()
            return redirect("all_other_items") 
    else:
        form = OtherForm()

    return render(request, "storage/add_other.html", {"form": form})

# HOME page
@login_required
def view_all_items(request):
    food_items = Food_items.objects.filter(
        family=request.user.profile.family, is_active=True, exp_date__gte=timezone.now().date()
    ).order_by("exp_date")
    other_items = Other_items.objects.filter(family=request.user.profile.family)
    return render(
        request, "storage/home.html", {"foods": food_items, "others": other_items,
                                       "family_name": request.user.profile.family.name,
                                       "weather_api_key": settings.WEATHER_API_KEY,}
    )


@login_required
def all_food(request):
    food_items = Food_items.objects.filter(
        family=request.user.profile.family, is_active=True).order_by("exp_date")

    return render(request,"storage/all_food_page.html",{"weather_api_key": settings.WEATHER_API_KEY,
                                                        "family_name": request.user.profile.family.name,
                                                        "foods": food_items, "profile":request.user.profile,
                                                        "today": now().date()})



@login_required
def all_other(request):
    other_items = Other_items.objects.filter(family=request.user.profile.family, is_active=True)
    return render(request, "storage/all_other_page.html",{"family_name": request.user.profile.family.name,
                                                          "others": other_items, "profile": request.user.profile,
                                                          "today": now().date(),
                                                        "weather_api_key": settings.WEATHER_API_KEY})

@login_required
def all_other_items(request):
    ordering = request.GET.get("ordering", "title")
    other_items = Other_items.objects.filter(
        family=request.user.profile.family,
        is_active=True
    ).order_by(ordering)

    context = {
        "other_items": other_items,
        "profile": request.user.profile,
        "today": now().date(),
        "weather_api_key": settings.WEATHER_API_KEY,
    }
    return render(request, "storage/all_other_items.html", context)

@login_required
def food_detail(request, slug):
    food = get_object_or_404(Food_items, slug=slug, family=request.user.profile.family)
    return render(request, "storage/food_detail.html", {"food": food})


@login_required
def other_detail(request, slug):
    other = get_object_or_404(
        Other_items, slug=slug, family=request.user.profile.family
    )
    return render(request, "storage/other_detail.html", {"other": other})

@login_required
@permission_required("storage.add_fooditems", raise_exception=True)
def choose_add_food(request):
    return render(request, "storage/choose_add_food.html")

@login_required
@permission_required("storage.add_otheritems", raise_exception=True)
def choose_add_other(request):
    return render(request, "storage/choose_add_other.html")

# search food
@login_required
@permission_required("storage.add_fooditems", raise_exception=True)
def search_food(request):
    if request.method == "POST":
        form = FoodForm(request.POST, request.FILES)
        if form.is_valid():
            food = form.save(commit=False)
            food.family = request.user.profile.family

            category_name = request.POST.get("category_name", "").strip()
            if category_name:
                # Some APIs return comma-separated categories; pick first
                first_category = category_name.split(",")[0].strip()
                if first_category:
                    category_obj, _ = Category.objects.get_or_create(name=first_category.title())
                    food.category = category_obj

            image_url = request.POST.get("image_url", "").strip()
            if image_url:
                try:
                    response = requests.get(image_url, timeout=5)
                    if response.status_code == 200:

                        ext = os.path.splitext(image_url)[-1].split("?")[0]
                        if ext.lower() not in [".jpg", ".jpeg", ".png"]:
                            ext = ".jpg"  
                        filename = f"{food.title.replace(' ', '_')}{ext}"
                        food.image.save(filename, ContentFile(response.content), save=False)
                except Exception as e:
                    print("Image download failed:", e)

            food.save()
            messages.success(request, f"{food.title} added successfully!")
            return redirect("search_food")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = FoodForm()

    return render(request, "storage/search_food.html", {"form": form})

@login_required
def search_openfoodfacts(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse({"results": []})

    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 10,
    }

    try:
        res = requests.get(url, params=params, timeout=5)
        data = res.json()
    except Exception:
        return JsonResponse({"results": []})

    results = []
    for product in data.get("products", []):
        results.append({
            "title": product.get("product_name"),
            "brand": product.get("brands"),
            "image": product.get("image_thumb_url"),
            "barcode": product.get("code"),
            "category": product.get("categories"),
        })

    return JsonResponse({"results": results})

# cant have @ gerneal permissions
@login_required
def profile_detail(request, id=None):
    """
    Show a user's profile:
    - Owners can view all profiles
    - Admins can view only users in their family
    - Regular users can view only themselves
    """
    current_user_profile = request.user.profile

    if id is None:
        profile = current_user_profile
    else:
        profile = get_object_or_404(Profile, id=id)

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
    profile = get_object_or_404(Profile, id)

    if request.user != profile.user and request.user.profile.role != Profile.Role.OWNER:
        return redirect("profile_detail", id=request.user.id)

    if request.method == "POST":
        profile.display_name = request.POST.get("display_name")
        if request.FILES.get("profile_pic"):
            profile.profile_pic = request.FILES["profile_pic"]
        if request.user.profile.role == Profile.Role.OWNER and request.POST.get("role"):
            profile.role = request.POST.get("role")
        profile.save()
        return redirect("profile_detail", id=profile.id)

    return render(request, "storage/edit_profile.html", {"profile": profile})

# start premisions edit
@login_required
@permission_required("storage.delete_fooditems", raise_exception=True)
def food_item_delete(request, slug):
    food = get_object_or_404(Food_items, slug=slug)
    if request.method == "POST":
        food.delete()
        return redirect(f"{reverse('all_food')}?success=1")

    return render(request, "storage/confirm_delete.html", {"food": food})


@login_required
@permission_required("storage.delete_otheritems", raise_exception=True)
def other_item_delete(request, slug):
    other = get_object_or_404(Other_items, slug=slug)
    if request.method == "POST":
        other.delete()
        return redirect(f"{reverse('all_other_items')}?success=1")

    return render(request, "storage/confirm_delete.html", {"other": other})


@login_required
@permission_required("storage.change_fooditems", raise_exception=True)
def food_edit(request, slug):
    food = get_object_or_404(Food_items, slug=slug)

    if request.user.profile.role != Profile.Role.OWNER and Profile.Role.ADMIN:
        return render(request, "403.html", status=403)

    if request.method == "POST":
        form = FoodForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('food-detail', args=[food.slug])}?success=1")
    else:
        form = FoodForm(instance=food)

    return render(
        request, "storage/add_food.html", {"form": form, "food": food, "is_edit": True}
    )


@login_required
@permission_required("storage.change_otheritems", raise_exception=True)
def other_edit(request, slug):
    other = get_object_or_404(Other_items, slug=slug)

    if request.user.profile.role != Profile.Role.OWNER and Profile.Role.ADMIN:
        return render(request, "403.html", status=403)

    if request.method == "POST":
        form = OtherForm(request.POST, request.FILES, instance=other)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('other-detail', args=[other.slug])}?success=1")
    else:
        form = OtherForm(instance=other)

    return render(
        request,
        "storage/add_other.html",
        {"form": form, "other": other, "is_edit": True},
    )

@login_required
def all_members(request):
    family = request.user.profile.family
    members = family.members.select_related("user").all()
    return render(request, "storage/members.html", {"family": family, "members": members})


@login_required
@permission_required("storage.edit_members", raise_exception=True)
def edit_member_view(request, member_id):
    member = get_object_or_404(
        Profile, id=member_id, family=request.user.profile.family
    )

    if request.method == "POST":
        new_role = request.POST.get("role")
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

@login_required
@permission_required("storage.change_category", raise_exception=True)
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk, family=request.user.profile.family)
    if category.is_default:
        messages.error(request, "Default categories cannot be deleted.")
    else:
        category.delete()
        messages.success(request, f"Category '{category.name}' deleted successfully.")
    return redirect("category")

@login_required
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

    return render(
        request,
        "storgae/manage_expiry.html",
        {"item": item, "form": form, "expiry": expiry},
    )

@login_required
@permission_required("storage.change_expired", raise_exception=True)
def delete_expiry(request, pk):
    expiry = get_object_or_404(
        ItemExpiry, pk=pk, item__family=request.user.profile.family
    )
    expiry.is_active = False
    expiry.save()
    messages.success(request, "Expiry tracking removed for this item.")
    return redirect("manage_expiry", item_id=expiry.item.id)

@login_required
@permission_required("storage.change_expired", raise_exception=True)
def delete_item(request, pk):
    item = get_object_or_404(Food_items, pk=pk, family=request.user.profile.family)
    item.is_active = False
    item.deleted_on = timezone.now()
    item.delete()
    messages.info(request, f"{item.title} has now been deleted")
    return redirect("all_food")

@login_required
@permission_required("storage.change_expired", raise_exception=True)
def restore_item(request, pk):
    item = get_object_or_404(
        Food_items, pk=pk, family=request.user.profile.family, is_active=False
    )
    item.is_active = True
    item.deleted_on = None
    item.restored = True
    item.save()
    messages.success(request, f"{item.title} restored successfully.")
    return redirect("all_food")

@login_required
def expired_items(request):
    user_family = request.user.profile.family
    today = timezone.now().date()

    expired_foods = Food_items.objects.filter(
        family=user_family, exp_date__lt=today, is_active=False
    ).order_by("exp_date")

    return render(request, "storage/expired_items.html", {"foods": expired_foods})


# see all the food in user's family
@login_required
def all_shopping_list(request):
    user_family = request.user.profile.family
    shop_lists = ShoppingList.objects.filter(family=user_family, is_active=True)
    return render(request, "storage/shoppingLists.html", {"lists": shop_lists})


# shopping
@login_required
def view_shopping_list(request, slug):
    shop_list = get_object_or_404(ShoppingList, slug=slug)
    items = shop_list.items.all()
    return render(
        request,
        "storage/shopping_list_detail.html",
        {"shop_list": shop_list, "items": items},
    )


@login_required
@permission_required("storage.add_shoppinglist", raise_exception=True)
def add_shopping_list(request):
    if request.method == "POST":
        form = ShoppingListForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            shopping_list = form.save(commit=False)
            shopping_list.family = request.user.profile.family
            shopping_list.created_by = request.user
            shopping_list.save()
            return redirect("all_shopping_list")
    else:
        form = ShoppingListForm(user=request.user)

    return render(request, "storage/add_shopping_list.html", {"form": form})


@login_required
@permission_required("storage.edit_shoppinglist", raise_exception=True)
def edit_shopping_list(request, slug):
    shopping_list = get_object_or_404(ShoppingList, slug=slug)
    if request.method == "POST":
        form = ShoppingListForm(request.POST, request.FILES, instance=shopping_list)
        if form.is_valid():
            form.save()
            return redirect("view_shopping_list", slug=shopping_list.slug)
    else:
        form = ShoppingListForm(instance=shopping_list)

    return render(
        request,
        "storage/edit_shopping_list.html",
        {"form": form, "shopping_list": shopping_list},
    )

@login_required
@permission_required("storage.delete_shoppinglist", raise_exception=True)
def delete_shopping_list(request, slug):
    shopping_list = get_object_or_404(ShoppingList, slug=slug)
    if request.method == "POST":
        shopping_list.delete()
        return redirect(f"{reverse('all_shopping_list')}?success=1")

    return render(
        request, "storage/confirm_delete.html", {"shopping_list": shopping_list}
    )

# may add feturte that admin can approve and chnage premissions
@login_required
def add_shopping_item(request, slug):
    shop_list = get_object_or_404(ShoppingList, slug=slug)
    if request.method == "POST":
        form = ShoppingItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.shopping_list = shop_list
            item.owner = request.user
            item.family = shop_list.family
            item.save()
            return redirect("view_shopping_list", slug=slug)
    else:
        form = ShoppingItemForm()
    return render(
        request, "storage/addShopItem.html", {"form": form, "shop_list": shop_list}
    )

@login_required
@permission_required("storage.edit_shoppinglist", raise_exception=True)
def edit_shopping_item(request, slug):
    item = get_object_or_404(Shopitems, slug=slug)
    if request.method == "POST":
        form = ShoppingItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("view_shopping_list", slug=item.shopping_list.slug)
    else:
        form = ShoppingItemForm(instance=item)
    return render(request, "storage/addShopItem.html", {"form": form, "item": item})

@login_required
@permission_required("storage.delete_shoppinglist", raise_exception=True)
def delete_shopping_item(request, slug):
    item = get_object_or_404(Shopitems, slug=slug)
    slug = item.shopping_list.slug
    item.delete()
    return redirect("view_shopping_list", slug=slug)

@login_required
@permission_required("storage.email", raise_exception=True)
def send_mail_shopping(request, slug):
    shopping_list = get_object_or_404(ShoppingList, slug=slug)
    
    family_members = shopping_list.family.members.all()
    recipient_emails = [member.user.email for member in family_members if member.user.email]

    message_lines = [f"Shopping List: {shopping_list.title}", f"Category: {shopping_list.category}", "", "Items:"]
    for item in shopping_list.items.all():
        item_name = item.item_name or (item.food_item.title if item.food_item else item.other_item.title)
        message_lines.append(f"- {item_name} | Type: {item.type} | Qty: {item.quantity} | Price: {item.price} | Purchased: {'Yes' if item.purchased else 'No'}")

    message_body = "\n".join(message_lines)

    result = None
    if request.method == "POST":
        subject = f"Shopping List: {shopping_list.title}"
        try:
            send_mail(
                subject,
                message_body,
                settings.EMAIL_HOST_USER,
                recipient_emails,
            )
            result = "Email sent successfully to all family members!"
        except Exception as e:
            result = f"Error sending email: {e}"

    return render(request, "storage/email/shoppingEmail.html", {
        "shopping_list": shopping_list,
        "recipient_emails": ", ".join(recipient_emails),
        "message_body": message_body,
        "result": result,
    })

# settings
@login_required
def user_settings(request):
    profile = request.user.profile

    if request.method == "POST":

        if "save_appearance" in request.POST:
            profile.theme = request.POST.get("theme", profile.theme)
            profile.font_size = int(request.POST.get("font_size", profile.font_size))
            profile.letter_spacing = float(request.POST.get("letter_spacing", profile.letter_spacing))
            profile.save()
            messages.success(request, "Appearance updated")

        elif "save_notifications" in request.POST:
            profile.notifications_enabled = "notifications" in request.POST
            profile.save()
            messages.success(request, "Notifications updated")

        return redirect("settings")

    return render(request, "storage/settings.html", {"profile": profile})

# email notificatyion to work when this happens
@login_required
def change_password(request):
    result = None

    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)

            subject = "Security alert: Password changed"
            message = (
                f"Hi {user.username},\n\n"
                "Your password was successfully changed.\n"
                "If this wasn't you, please contact support immediately."
            )

            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [user.email],
                )
                result = "Password changed and email notification sent."
            except Exception as e:
                result = f"Password changed, but email failed: {e}"

            messages.success(request, result)
            return redirect("settings")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "storage/change_password.html", {
        "form": form,
        "result": result,
    })

@login_required
def delete_account(request):
    result = None

    if request.method == "POST":
        user = request.user
        email = user.email
        username = user.username

        logout(request)

        try:
            send_mail(
                subject="Account deletion confirmation",
                message=(
                    f"Hi {username},\n\n"
                    "Your account has been permanently deleted.\n"
                    "If this was a mistake, please contact support."
                ),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
            )
            result = "Account deleted and confirmation email sent."
        except Exception as e:
            result = f"Account deleted, but email failed: {e}"

        user.delete()
        messages.success(request, result)
        return redirect("login")

    return render(request, "storage/confirm_account_deletion.html", {
        "result": result
    })


@login_required
def change_email(request):
    user = request.user

    if request.method == "POST":
        form = EmailChangeForm(user, request.POST)
        if form.is_valid():
            new_email = form.cleaned_data["new_email"]
            old_email = user.email

            user.email = new_email
            user.save()

            # Email notification
            send_mail(
                subject="Email address changed",
                message=(
                    f"Hi {user.profile.display_name},\n\n"
                    f"Your email address was changed from {old_email} to {new_email}.\n"
                    "If this wasn’t you, please contact support immediately."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[new_email],
                fail_silently=True,
            )

            messages.success(request, "Email updated successfully.")
            return redirect("settings")
    else:
        form = EmailChangeForm(user)

    return render(request, "storage/change_email.html", {"form": form})
