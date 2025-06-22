from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date, timedelta
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver 
from django.contrib.auth.models import Permission, AbstractUser
from django.contrib.contenttypes.models import ContentType

# food_item models
class Food_items(models.Model):
    image = models.ImageField(default="public_image/items/default_food.jpg", 
                              upload_to="public_image/items/actual_items/food")
    brand = models.CharField(blank=True, max_length=512)
    title = models.CharField(unique=False, blank=False, max_length=512)
    quantity =  models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(50)])
    exp_date = models.DateField(
        null=True, blank=True,
        validators=[
            MaxValueValidator(date.today() + timedelta(days=5*365))  # 5 years into the future
        ]
    )
    slug = models.SlugField(editable=False, unique=True)
    
    
    def year(self):
        if self.exp_date:
            return self.exp_date.year
        return "Unknown"
    
    
    class Meta:
        unique_together = ('brand', 'title', 'quantity')

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.brand}-'{self.title}'-({self.quantity})")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title}, expired({self.exp_date})"
    

# non food items to add 
class Other_items(models.Model):
    image = models.ImageField(default="public_image/items/default_image.jpg", 
                              upload_to="public_image/items/actual_items/other")
    brand = models.CharField(blank=True, max_length=512)
    title = models.CharField(unique=False, blank=False, max_length=512)
    quantity =  models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(50)])
    slug = models.SlugField(editable=False, unique=True)
    

    
    class Meta:
        unique_together = ('brand', 'title', 'quantity')

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.brand}-'{self.title}'-({self.quantity})")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title}"
    

# user model
class User(models.Model):
    class Role(models.TextChoices):
        ADMIN = "admin", ("Admin")
        USER = "user", ("User")

    profile_pic = models.ImageField(default="profile_pics/default_profile_pic.jpg", 
                                    upload_to="profile_pic/personal_images")
    family = models.ForeignKey("family", on_delete=models.CASCADE, related_name="members")
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    display_name = models.CharField(max_length=512)
    role = models.CharField(max_length=10, choices=Role.choices)

    def __str__(self):
        return f"{self.display_name} ({self.role})"



# user permissions set
@receiver(post_save, sender=User)
def assign_permissions(sender, instance, created, **kwargs):
    if created:
        food_type = ContentType.objects.get_for_model(Food_items)
        other_type = ContentType.objects.get_for_model(Other_items)

        if instance.role == User.Role.ADMIN:
            perms = Permission.objects.filter(
                content_type__in=[food_type, other_type],
                codename__in=[
                    "add_fooditems", "change_fooditems", "delete_fooditems", "view_fooditems",
                    "add_otheritems", "change_otheritems", "delete_otheritems", "view_otheritems"
                ]
            )
        else:  # role is USER
            perms = Permission.objects.filter(
                content_type__in=[food_type, other_type],
                codename__in=[
                    "change_fooditems", "view_fooditems",
                    "change_otheritems", "view_otheritems"
                ]
            )
        instance.user_permissions.set(perms)

# family model
class Family(models.Model):
    name = models.CharField(unique=False, blank=False, max_length=512)
    number = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(50)])
    
    def __str__(self):
        return f"{self.name}, has {self.number} members"