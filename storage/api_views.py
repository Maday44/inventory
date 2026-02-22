from django.utils import timezone
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated

from .models import Family, Food_items, Other_items, User
from .serializers import FamSerializer, FoodSerializer, OtherSerializer, UserSerializer


class FoodViewSet(viewsets.ModelViewSet):
    serializer_class = FoodSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [OrderingFilter]
    ordering_fields = ["title", "quantity", "exp_date", "price"]
    ordering = ["exp_date"]

    def get_queryset(self):
        user_family = self.request.user.profile.family
        return Food_items.objects.filter(
            family=user_family,
            is_active=True,
        )


class OtherViewSet(viewsets.ModelViewSet):
    serializer_class = OtherSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ["title", "quantity", "price"]  # add price if you have it
    ordering = ["title"]

    def get_queryset(self):
        user_family = self.request.user.profile.family
        return Other_items.objects.filter(family=user_family)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class FamViewSet(viewsets.ModelViewSet):
    queryset = Family.objects.all()
    serializer_class = FamSerializer
