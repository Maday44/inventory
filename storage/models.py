from datetime import date, timedelta

from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
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


def generate_unique_slug(instance, value, slug_field="slug"):
    ModelClass = instance.__class__

    base_slug = slugify(value)
    slug = base_slug
    counter = 1

    lookup = {
        slug_field: slug,
        "family": instance.family,
    }

    while ModelClass.objects.filter(**lookup).exists():
        slug = f"{base_slug}-{counter}"
        lookup[slug_field] = slug
        counter += 1

    return slug


class Food_items(models.Model):
    barcode = models.CharField(max_length=32, blank=True, null=True)
    image = models.ImageField(
        default="items/default_food.jpg", upload_to="items/actual_items/food"
    )
    brand = models.CharField(blank=True, max_length=512)
    title = models.CharField(blank=False, max_length=512)
    quantity = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)]
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
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
        if self.title:
            self.title = self.title.title()
        self.slug = slugify(f"{self.brand}-{self.title}-{self.quantity}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.category}) - exp-date({self.exp_date})"


class Other_items(models.Model):
    image = models.ImageField(
        default="items/default_image.jpg",
        upload_to="items/actual_items/other",
    )
    brand = models.CharField(blank=True, max_length=512)
    title = models.CharField(blank=False, max_length=512)
    quantity = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)]
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
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
        if self.title:
            self.title = self.title.title()
        self.slug = slugify(f"{self.brand}-{self.title}-{self.quantity}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.category})"


class Family(models.Model):
    name = models.CharField(blank=False, max_length=512)

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.title()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}, has {self.members.count()} members"


class Profile(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        USER = "user", "User"

    THEME_COLOUR = [
        ("light", "Light"),
        ("dark", "Dark"),
        ("system", "System"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_pic = models.ImageField(
        default="profile_pics/default_profile_pic.jpg",
        upload_to="profile_pic/personal_images",
    )
    family = models.ForeignKey(
        "Family", on_delete=models.CASCADE, related_name="members", null=True
    )
    display_name = models.CharField(max_length=512)
    role = models.CharField(max_length=10, choices=Role.choices)

    theme = models.CharField(max_length=10, choices=THEME_COLOUR, default="light")
    notifications_enabled = models.BooleanField(default=True)
    font_size = models.PositiveSmallIntegerField(default=16)
    letter_spacing = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

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
    )  

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
    slug = models.SlugField(blank=False, null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["family", "slug"], name="unique_shoppinglist_slug_per_family"
            )
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(
                self,
                source_field="title",
            )
        super().save(*args, **kwargs)

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

    item_name = models.CharField(max_length=512, blank=True)
    family = models.ForeignKey(
        Family, null=True, on_delete=models.CASCADE, related_name="shop_items"
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shop_items")
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    purchased = models.BooleanField(default=False)
    slug = models.SlugField(blank=False, null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["family", "slug"],
                name="unique_shopitem_slug_per_family",
            )
        ]

    def __str__(self):
        name = (
            self.item_name
            or (self.food_item.title if self.food_item else None)
            or (self.other_item.title if self.other_item else None)
            or "Unnamed"
        )
        return f"{name} (x{self.quantity})"

    def get_display_name(self):
        if self.item_name:
            return self.item_name
        if self.food_item:
            return self.food_item.title
        if self.other_item:
            return self.other_item.title
        return "item"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_value = self.get_display_name()
            self.slug = generate_unique_slug(
                self,
                base_value,
            )
        super().save(*args, **kwargs)

    def clean(self):
        """Ensure that exactly one item source is set."""
        from django.core.exceptions import ValidationError

        # Can't have both food_item and other_item at once
        if self.food_item and self.other_item:
            raise ValidationError("Select only one item type: food OR other.")

        if not (self.food_item or self.other_item or self.item_name.strip()):
            raise ValidationError("Provide either a linked item or a manual item name.")


@receiver(post_save, sender=User)
def assign_permissions(sender, instance, created, **kwargs):
    """
    Assign permissions to a user after creation.
    Does NOT create a Profile if it already exists to avoid UNIQUE constraint errors.
    """
    if not created:
        return 

    try:
        profile = instance.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(
            user=instance,
            display_name=instance.username,
            family=None,  
            role=Profile.Role.USER,
        )

    food_type = ContentType.objects.get_for_model(Food_items)
    other_type = ContentType.objects.get_for_model(Other_items)
    shoppinglist_type = ContentType.objects.get_for_model(ShoppingList)

    if profile.role in [Profile.Role.ADMIN, Profile.Role.OWNER]:
        codenames = [
            "add_food_items",
            "change_food_items",
            "delete_food_items",
            "view_food_items",
            "add_other_items",
            "change_other_items",
            "delete_other_items",
            "view_other_items",
            "add_shopping_list",
            "change_shopping_list",
            "edit_members",
            "change_category",
            "change_expired",
            "delete_shopping_list",
            "view_profile_detail",
            "add_category",
            "delete_category",
            "add_shoppingcategory",
            "change_shoppingcategory",
            "delete_shoppingcategory",
            "change_itemexpiry",
            "delete_itemexpiry",
            "add_shopitems",
            "change_shopitems",
            "delete_shopitems",
            "change_family",
            "delete_family",
            "email",
        ]
        # <QuerySet ['add_profile', 'change_profile', 'delete_profile', 'view_profile']>

        perms = Permission.objects.filter(
            content_type__in=[food_type, other_type, shoppinglist_type],
            codename__in=codenames,
        )
    else:
        codenames = [
            "change_food_items",
            "view_food_items",
            "change_other_items",
            "view_other_items",
        ]
        perms = Permission.objects.filter(
            content_type__in=[food_type, other_type],
            codename__in=codenames,
        )

    # Assign permissions to the user
    instance.user_permissions.set(perms)
