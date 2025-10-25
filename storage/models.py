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
    image = models.ImageField(
        default="items/default_food.jpg",   
        upload_to="items/actual_items/food" 
    )
    brand = models.CharField(blank=True, max_length=512)
    title = models.CharField(unique=False, blank=False, max_length=512)
    quantity =  models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(50)])
    exp_date = models.DateField(
        null=True, blank=True,
        validators=[MaxValueValidator(date.today() + timedelta(days=5*365))]
    )
    #catorigies = models.CharField(blank=True, max_length=512)
    slug = models.SlugField(editable=False, unique=True)
    
    
    # link to family
    family = models.ForeignKey("Family", on_delete=models.CASCADE, related_name="food_items")

    class Meta:
        unique_together = ('brand', 'title', 'quantity', 'family')  # include family in uniqueness

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.brand}-'{self.title}'-({self.quantity})")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title}, expired({self.exp_date})"

# non-food items
class Other_items(models.Model):
    image = models.ImageField(default="public_image/items/default_image.jpg", 
                              upload_to="public_image/items/actual_items/other")
    brand = models.CharField(blank=True, max_length=512)
    title = models.CharField(unique=False, blank=False, max_length=512)
    quantity =  models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(50)])
    #catorigies = models.CharField(blank=True, max_length=512)
    slug = models.SlugField(editable=False, unique=True)
    
    # link to family
    family = models.ForeignKey("Family", on_delete=models.CASCADE, related_name="other_items")

    class Meta:
        unique_together = ('brand', 'title', 'quantity', 'family')

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.brand}-'{self.title}'-({self.quantity})")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title}"


# user/profile model
class Profile(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner","Owner"
        ADMIN = "admin", "Admin"
        USER = "user", "User"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_pic = models.ImageField(default="profile_pics/default_profile_pic.jpg", upload_to="profile_pic/personal_images")
    family = models.ForeignKey("Family", on_delete=models.CASCADE, related_name="members")
    display_name = models.CharField(max_length=512)
    role = models.CharField(max_length=10, choices=Role.choices)

    def __str__(self):
        return f"{self.display_name} ({self.role})"

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
                    "add_fooditems", "change_fooditems", "delete_fooditems", "view_fooditems",
                    "add_otheritems", "change_otheritems", "delete_otheritems", "view_otheritems"
                ]
            )
        else:
            perms = Permission.objects.filter(
                content_type__in=[food_type, other_type],
                codename__in=[
                    "change_fooditems", "view_fooditems",
                    "change_otheritems", "view_otheritems"
                ]
            )
        instance.user_permissions.set(perms)
        
        
        
'''
@receiver(post_save, sender=MusicManagerUser)
def assign_permissions(sender, instance, created, **kwargs):
    if created:
        permissions = []
        album_content_type = ContentType.objects.get_for_model(Album)
        song_content_type = ContentType.objects.get_for_model(Song)

        if instance.role == MusicManagerUser.Role.EDITOR:
            permissions += Permission.objects.filter(
                content_type__in=[album_content_type, song_content_type],
                codename__in=["add_album", "change_album", "delete_album", "view_album",
                              "add_song", "change_song", "delete_song", "view_song"]
            )
        elif instance.role == MusicManagerUser.Role.VIEWER:
            permissions += Permission.objects.filter(
                content_type=album_content_type, codename="view_album"
            )
            permissions += Permission.objects.filter(
                content_type=song_content_type, codename="view_song"
            )
        elif instance.role == MusicManagerUser.Role.ARTIST:
            permissions += Permission.objects.filter(
                content_type=album_content_type, codename="view_album"
            )
            permissions += Permission.objects.filter(
                content_type=song_content_type, codename="view_song"
            )

        instance.user.user_permissions.add(*permissions)

'''        


# family model
class Family(models.Model):
    name = models.CharField(unique=False, blank=False, max_length=512)
    
    def __str__(self):
        return f"{self.name}, has {self.members.count()} members"