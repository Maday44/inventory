from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from .models import Food_items, Other_items, Profile
from django.contrib.auth import logout
from django.http import HttpResponseForbidden, HttpResponse
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
import json

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

def auth0_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get("user"):
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper

@auth0_login_required
def view_all_items(request):
    # ------------------ Check Auth0 session ------------------
    user = request.session.get("user")
    if not user:
        # Not logged in via Auth0 → redirect to login
        return redirect(reverse("login"))

    # ------------------ Get user info from Auth0 ------------------
    user_info = user.get("userinfo", {})
    given_name = user_info.get("given_name", "User")
    email = user_info.get("email", "")

    # ------------------ Your original logic ------------------
    try:
        user_family = request.user.profile.family
        food_items = Food_items.objects.filter(
            family=user_family,
            is_active=True,
            exp_date__gte=timezone.now().date()
        ).order_by("exp_date")
        other_items = Other_items.objects.filter(family=user_family)
    except Exception:
        # If user does not have a family/profile
        food_items = []
        other_items = []

    # ------------------ Render template ------------------
    return render(
        request,
        "storage/home.html",
        {
            "foods": food_items,
            "others": other_items,
            "user_info": user_info,  # Auth0 info for welcome message, profile picture
        },
    )


# ------------------ Login ------------------
def login(request):
    return oauth.auth0.authorize_redirect(
        request,
        request.build_absolute_uri(reverse("callback"))
    )

# ------------------ Callback ------------------
def callback(request):
    try:
        token = oauth.auth0.authorize_access_token(request)
        request.session["user"] = token
        return redirect(reverse("index"))
    except Exception:
        # Could not authorize → show "no account" page
        return redirect(reverse("no_account"))

# ------------------ Logout ------------------
def logout(request):
    request.session.clear()
    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("index")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        )
    )

# ------------------ Optional no account page ------------------
def no_account(request):
    return render(request, "storage/no_account.html")

# remove "@login_required" when auth0 is working
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
            other.family = request.user.profile.family  # assign user's family
            other.save()
            return redirect("all_other_items")  # redirect to food list
    else:
        form = OtherForm()

    # Render a dedicated 'add food' template (not food_detail)
    return render(request, "storage/add_other.html", {"form": form})

# remove?
@login_required
# home page: show all items in the user's family
def view_all_items(request):
    user_family = request.user.profile.family
    food_items = Food_items.objects.filter(
        family=user_family, is_active=True, exp_date__gte=timezone.now().date()
    ).order_by("exp_date")
    other_items = Other_items.objects.filter(family=user_family)
    return render(
        request, "storage/home.html", {"foods": food_items, "others": other_items}
    )


# see all the food in user's family
@login_required
def all_food(request):
    return render(request,"storage/allFoodPage.html")


# see all other items in user's family
@login_required
def all_other(request):
    return render(request, "storage/allOtherPage.html")


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
def choose_add_food(request):
    return render(request, "storage/choose_add_food.html")

@login_required
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

# change
@login_required
def custom_logout(request):
    if request.method == "POST":
        logout(request)
        return render(request, "logout_thanks.html")  # thank-you page
    else:
        return redirect("/")  # redirect GET requests away

# here delete like shopiing list
# dlete comment later
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
@permission_required("storage.change_fooditems", raise_exception=True)
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

    return render(
        request, "storage/add_food.html", {"form": form, "food": food, "is_edit": True}
    )


@login_required
@permission_required("storage.change_otheritems", raise_exception=True)
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

    return render(
        request,
        "storage/add_other.html",
        {"form": form, "other": other, "is_edit": True},
    )

@login_required
def all_members(request):
    family = request.user.profile.family
    members = family.members.select_related("user").all()
    return render(
        request, "storage/members.html", {"family": family, "members": members}
    )

@login_required
def member_detail(request):
    pass


@login_required
def edit_member_view(request, member_id):
    member = get_object_or_404(
        Profile, id=member_id, family=request.user.profile.family
    )

    if request.method == "POST":
        new_role = request.POST.get("role")
        if request.user.profile.role in [
            "owner",
            "admin",
        ]:  # only admins/owners can edit
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
def delete_expiry(request, pk):
    expiry = get_object_or_404(
        ItemExpiry, pk=pk, item__family=request.user.profile.family
    )
    expiry.is_active = False
    expiry.save()
    messages.success(request, "Expiry tracking removed for this item.")
    return redirect("manage_expiry", item_id=expiry.item.id)

@login_required
def delete_item(request, pk):
    item = get_object_or_404(Food_items, pk=pk, family=request.user.profile.family)
    item.is_active = False
    item.deleted_on = timezone.now()
    item.delete()
    messages.info(request, f"{item.title} has now been deleted")
    return redirect("all_food")

@login_required
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



def edit_shopping_list(request, slug):
    shopping_list = get_object_or_404(ShoppingList, slug=slug)

    if request.user.profile.role not in [Profile.Role.OWNER, Profile.Role.ADMIN]:
        return HttpResponseForbidden("Access Denied")

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

def delete_shopping_list(request, slug):
    shopping_list = get_object_or_404(ShoppingList, slug=slug)
    if request.user.profile.role != Profile.Role.OWNER and Profile.Role.ADMIN:
        return HttpResponseForbidden("Access Denied")

    if request.method == "POST":
        shopping_list.delete()
        return redirect(f"{reverse('all_shopping_list')}?success=1")

    return render(
        request, "storage/confirm_delete.html", {"shopping_list": shopping_list}
    )


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


def delete_shopping_item(request, slug):
    item = get_object_or_404(Shopitems, slug=slug)
    slug = item.shopping_list.slug
    item.delete()
    return redirect("view_shopping_list", slug=slug)

#send email shopping list
def send_mail_shopping(request, slug):
    # Get the shopping list
    shopping_list = get_object_or_404(ShoppingList, slug=slug)
    
    # Get all family members
    family_members = shopping_list.family.members.all()
    recipient_emails = [member.user.email for member in family_members if member.user.email]

    # Build the shopping list message
    message_lines = [f"Shopping List: {shopping_list.title}", f"Category: {shopping_list.category}", "", "Items:"]
    for item in shopping_list.items.all():
        item_name = item.item_name or (item.food_item.title if item.food_item else item.other_item.title)
        message_lines.append(f"- {item_name} | Type: {item.type} | Qty: {item.quantity} | Price: {item.price} | Purchased: {'Yes' if item.purchased else 'No'}")

    message_body = "\n".join(message_lines)

    # Send email on POST request
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