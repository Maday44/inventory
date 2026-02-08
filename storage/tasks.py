from django.core.mail import send_mail
from django.utils import timezone

from .models import Food_items


def check_expired_items():
    today = timezone.now().date()
    expired_items = Food_items.objects.filter(
        is_active=True, exp_date__lt=today, restored=False
    )

    for item in expired_items:
        item.is_active = False
        item.deleted_on = timezone.now()
        item.save()

        family_member = item.family.memberships.first()
        # email function needs work
        if family_member:
            family_email = family_member.profile.user.email
            send_mail(
                subject=f"'{item.title}' has expired!",
                message=f"Your item '{item.title}' expired on {item.exp_date}.",
                from_email="noreply@homeinventory.com",
                recipient_list=[family_email],
            )
