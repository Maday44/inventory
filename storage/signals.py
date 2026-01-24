from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile, assign_permissions


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance, display_name=instance.username, role="user"
        )


@receiver(post_save, sender=User)
def assign_permissions(sender, instance, created, **kwargs):
    if not created:
        return

    profile, _ = Profile.objects.get_or_create(
        user=instance,
        defaults={
            "display_name": instance.username,
            "family": None,
            "role": Profile.Role.USER,
        }
    )

    assign_permissions(instance, profile)
