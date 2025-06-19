
from .models import Food_items, Other_items, User, Family
from .serializers import UserSerializer, FamSerializer, FoodSerializer, OtherSerializer
from rest_framework import viewsets

class FoodViewSet(viewsets.ModelViewSet):
    queryset = Food_items.objects.all()
    serializer_class = FoodSerializer
    
class OtherViewSet(viewsets.ModelViewSet):
    queryset = Other_items.objects.all()
    serializer_class = OtherSerializer
    
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
class FamViewSet(viewsets.ModelViewSet):
    queryset = Family.objects.all()
    serializer_class = FamSerializer
    