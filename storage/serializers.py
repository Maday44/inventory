from rest_framework import serializers
from .models import Food_items, Other_items, User, Family


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class FamSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Family
        fields = '__all__'
        
        
class FoodSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Food_items
        fields = '__all__'
    
    

class OtherSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Other_items
        fields = '__all__'
    
