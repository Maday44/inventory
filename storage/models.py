from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date, timedelta
from django.utils.text import slugify
from django.contrib.auth.models import User, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now


class Category(models.Model):
    DEFAULT_CATEGORIES = [
        "Fruits",
        "Vegetables",
        "Meat & Poultry",
        "Dairy",
        "Snacks",
        "Beverages",
        "Canned Goods",
        "Frozen Foods",
        "Condiments",
        "Cleaning Supplies",
        "Toiletries",
        "Stationery",
        "Electronics",
        "Clothing",
        "Miscellaneous",
    ]

    name = models.CharField(max_length=255, unique=False)
    is_default = models.BooleanField(default=False)
    family = models.ForeignKey(
        "Family",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="categories",
    )

    class Meta:
        unique_together = ("name", "family")

    def __str__(self):
        return f"{self.name} {'(default)' if self.is_default else ''}"

    @classmethod
    def create_default_categories(cls):
        for cat in cls.DEFAULT_CATEGORIES:
            cls.objects.get_or_create(name=cat, is_default=True, family=None)


class ShoppingCategory(models.Model):
    DEFAULT_SHOP_CATEGORIES = [
        "Weekly Food Shop",
        "Bits and Bobs",
        "Christmas",
        "Easter",
        "DIY",
        "Hangout",
        "Party",
        "Birthdays",
        "Gifts",
        "Clothes",
    ]

    name = models.CharField(max_length=255, unique=False)
    is_default = models.BooleanField(default=False)
    family = models.ForeignKey(
        "Family",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="shopping_categories",
    )

    class Meta:
        unique_together = ("name", "family")

    def __str__(self):
        return f"{self.name} {'(default)' if self.is_default else ''}"

    @classmethod
    def create_default_categories(cls):
        for cat in cls.DEFAULT_SHOP_CATEGORIES:
            cls.objects.get_or_create(name=cat, is_default=True, family=None)


class Food_items(models.Model):
    image = models.ImageField(
        default="items/default_food.jpg", upload_to="items/actual_items/food"
    )
    brand = models.CharField(blank=True, max_length=512)
    title = models.CharField(blank=False, max_length=512)
    quantity = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)]
    )
    exp_date = models.DateField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(date.today() + timedelta(days=5 * 365))],
    )
    slug = models.SlugField(editable=False, unique=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="food_items",
    )

    family = models.ForeignKey(
        "Family", on_delete=models.CASCADE, related_name="food_items"
    )
    is_active = models.BooleanField(default=True)
    deleted_on = models.DateTimeField(null=True, blank=True)
    restored = models.BooleanField(default=False)

    class Meta:
        unique_together = ("brand", "title", "quantity", "family")

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.brand}-{self.title}-{self.quantity}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.category}) - exp-date({self.exp_date})"


class Other_items(models.Model):
    image = models.ImageField(
        default="public_image/items/default_image.jpg",
        upload_to="public_image/items/actual_items/other",
    )
    brand = models.CharField(blank=True, max_length=512)
    title = models.CharField(blank=False, max_length=512)
    quantity = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)]
    )
    slug = models.SlugField(editable=False, unique=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="other_items",
    )

    family = models.ForeignKey(
        "Family", on_delete=models.CASCADE, related_name="other_items"
    )
    is_active = models.BooleanField(default=True)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("brand", "title", "quantity", "family")

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.brand}-{self.title}-{self.quantity}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.category})"


class Family(models.Model):
    name = models.CharField(blank=False, max_length=512)

    def __str__(self):
        return f"{self.name}, has {self.members.count()} members"


class Profile(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        USER = "user", "User"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_pic = models.ImageField(
        default="profile_pics/default_profile_pic.jpg",
        upload_to="profile_pic/personal_images",
    )
    family = models.ForeignKey(
        "Family", on_delete=models.CASCADE, related_name="members"
    )
    display_name = models.CharField(max_length=512)
    role = models.CharField(max_length=10, choices=Role.choices)

    def __str__(self):
        return f"{self.display_name} ({self.role})"


class ItemExpiry(models.Model):
    item = models.ForeignKey(
        "Food_items", on_delete=models.CASCADE, related_name="expiry_records"
    )
    exp_date = models.DateField(null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(
        default=True
    )  # allows re-adding or reactivating expiry tracking

    def is_expired(self):
        return self.exp_date and self.exp_date < date.today()

    def days_until_expiry(self):
        return (self.exp_date - date.today()).days if self.exp_date else None

    def __str__(self):
        return f"{self.item.title} expires {self.exp_date}"


class ShoppingList(models.Model):
    title = models.CharField(blank=False, max_length=512)
    category = models.ForeignKey(
        ShoppingCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shopping_List",
    )
    family = models.ForeignKey(
        Family, null=True, on_delete=models.CASCADE, related_name="shopping_lists"
    )
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="shopping_lists"
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    completed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, blank=False, null=False)

    def __str__(self):
        return f"{self.title} ({self.category}) created by {self.created_by}"


class Shopitems(models.Model):

    class Types(models.TextChoices):
        FOOD = "food", "Food"
        OTHER = "other", "Other"

    shopping_list = models.ForeignKey(
        ShoppingList, on_delete=models.CASCADE, related_name="items"
    )
    type = models.CharField(max_length=10, choices=Types.choices)

    # Optional links to predefined items
    food_item = models.ForeignKey(
        Food_items,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shop_entries",
    )
    other_item = models.ForeignKey(
        Other_items,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shop_entries",
    )

    # Manual entry name (if not using existing item)
    item_name = models.CharField(max_length=512, blank=True)
    family = models.ForeignKey(
        Family, null=True, on_delete=models.CASCADE, related_name="shop_items"
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shop_items")
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    purchased = models.BooleanField(default=False)

    def __str__(self):
        name = (
            self.item_name
            or (self.food_item.title if self.food_item else None)
            or (self.other_item.title if self.other_item else None)
            or "Unnamed"
        )
        return f"{name} (x{self.quantity})"

    def clean(self):
        """Ensure that exactly one item source is set."""
        from django.core.exceptions import ValidationError

        # Can't have both food_item and other_item at once
        if self.food_item and self.other_item:
            raise ValidationError("Select only one item type: food OR other.")

        # Must have at least one name source
        if not (self.food_item or self.other_item or self.item_name.strip()):
            raise ValidationError("Provide either a linked item or a manual item name.")


@receiver(post_save, sender=User)
def assign_permissions(sender, instance, created, **kwargs):
    if created:
        profile = instance.profile
        food_type = ContentType.objects.get_for_model(Food_items)
        other_type = ContentType.objects.get_for_model(Other_items)

        if profile.role in [Profile.Role.ADMIN, Profile.Role.OWNER]:
            perms = Permission.objects.filter(
                content_type__in=[food_type, other_type],
                codename__in=[
                    "add_fooditems",
                    "change_fooditems",
                    "delete_fooditems",
                    "view_fooditems",
                    "add_otheritems",
                    "change_otheritems",
                    "delete_otheritems",
                    "view_otheritems",
                ],
            )
        else:
            perms = Permission.objects.filter(
                content_type__in=[food_type, other_type],
                codename__in=[
                    "change_fooditems",
                    "view_fooditems",
                    "change_otheritems",
                    "view_otheritems",
                ],
            )
        instance.user_permissions.set(perms)
