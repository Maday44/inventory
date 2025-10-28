
from .models import Food_items, Other_items, User, Family
from .serializers import UserSerializer, FamSerializer, FoodSerializer, OtherSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone


class FoodViewSet(viewsets.ModelViewSet):
    serializer_class = FoodSerializer
    permission_classes = [IsAuthenticated]
    queryset = Food_items.objects.all()#
    
    

    def get_queryset(self):
        user_family = self.request.user.profile.family
        return Food_items.objects.filter(
            family=user_family,
            is_active=True,
            exp_date__gte=timezone.now().date()
        ).order_by('exp_date')

    def get_queryset(self):
        user_family = self.request.user.profile.family
        return Food_items.objects.filter(
            family=user_family,
            is_active=True
        ).order_by('exp_date')

    
    
class OtherViewSet(viewsets.ModelViewSet):
    queryset = Other_items.objects.all()
    serializer_class = OtherSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user_family = self.request.user.profile.family
        return Other_items.objects.filter(family=user_family)
    
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
class FamViewSet(viewsets.ModelViewSet):
    queryset = Family.objects.all()
    serializer_class = FamSerializer
    