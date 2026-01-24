from rest_framework import serializers

from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class FamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = "__all__"


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food_items
        fields = "__all__"


class OtherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Other_items
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]

    def create(self, validated_data):
        validated_data["family"] = self.context["request"].user.profile.family
        return super().create(validated_data)


class ShopItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shopitems
        fields = "__all__"


class ShopListSerializer(serializers.ModelSerializer):
    items = ShopItemSerializer(many=True, read_only=True)

    class Meta:
        model = ShoppingList
        fields = "__all__"
