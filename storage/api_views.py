
from .models import Food_items, Other_items, User, Family
from .serializers import UserSerializer, FamSerializer, FoodSerializer, OtherSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

class FoodViewSet(viewsets.ModelViewSet):
    queryset = Food_items.objects.all()
    serializer_class = FoodSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only show items belonging to the logged-in user's family
        user_family = self.request.user.profile.family
        return Food_items.objects.filter(family=user_family)
    
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
    