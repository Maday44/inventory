from django import forms
from .models import *


class FoodForm(forms.ModelForm):
    class Meta:
        model = Food_items
        fields = ["title", "category", "brand", "quantity","price", "exp_date", "image"]
        widgets = {
            "exp_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
        }
        labels = {
            "category": "Category",
            "title": "Name",
            "brand": "Brand",
            "quantity": "Amount / Quantity",
            "price":"Price",
            "exp_date": "Expiry Date",
            "image": "Upload Image",
        }


class OtherForm(forms.ModelForm):
    class Meta:
        model = Other_items
        fields = ["title", "category", "brand", "quantity", "price","image"]
        labels = {
            "category": "Category",
            "title": "Name",
            "brand": "Brand",
            "quantity": "Amount / Quantity",
            "price":"Price",
            "image": "Upload Image",
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter category name"}
            ),
        }


class ItemExpiryForm(forms.ModelForm):
    class Meta:
        model = ItemExpiry
        fields = ["exp_date"]
        widgets = {"exp_date": forms.DateInput(attrs={"type": "date"})}


class ShoppingListForm(forms.ModelForm):
    class Meta:
        model = ShoppingList
        fields = ["title","category","budget","completed"]
    
    def __init__(self, *args, **kwargs):
        # pop 'user' from kwargs if present
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)



class ShoppingItemForm(forms.ModelForm):
    class Meta:
        model = Shopitems
        fields = ["type","food_item","other_item","item_name","quantity","price","purchased"]
