from django import forms

from .models import *


class FoodForm(forms.ModelForm):
    class Meta:
        model = Food_items
        fields = [
            "title",
            "category",
            "brand",
            "quantity",
            "price",
            "exp_date",
            "image",
        ]
        widgets = {
            "exp_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
        }
        labels = {
            "barcode": "Barcode",
            "category": "Category",
            "title": "Name",
            "brand": "Brand",
            "quantity": "Amount / Quantity",
            "price": "Price",
            "exp_date": "Expiry Date",
            "image": "Upload Image",
        }


class OtherForm(forms.ModelForm):
    class Meta:
        model = Other_items
        fields = ["title", "category", "brand", "quantity", "price", "image"]
        labels = {
            "category": "Category",
            "title": "Name",
            "brand": "Brand",
            "quantity": "Amount / Quantity",
            "price": "Price",
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
        fields = ["title", "category", "budget", "completed"]

    def __init__(self, *args, **kwargs):
        # pop 'user' from kwargs if present
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)


class ShoppingItemForm(forms.ModelForm):
    class Meta:
        model = Shopitems
        fields = [
            "type",
            "food_item",
            "other_item",
            "item_name",
            "quantity",
            "price",
            "purchased",
        ]


class EmailChangeForm(forms.Form):
    new_email = forms.EmailField(label="New email", required=True)
    password = forms.CharField(
        label="Current password", widget=forms.PasswordInput, required=True
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data["password"]
        if not self.user.check_password(password):
            raise forms.ValidationError("Incorrect password.")
        return password

    def clean_new_email(self):
        email = self.cleaned_data["new_email"]
        if email == self.user.email:
            raise forms.ValidationError("This is already your email.")
        return email


CODENAMES = [
    "add_food_items",
    "change_food_items",
    "delete_food_items",
    "add_other_items",
    "change_other_items",
    "delete_other_items",
    "add_shopping_list",
    "view_profile_detail",
    "edit_members",
    "change_category",
    "add_category",
    "delete_category",
    "add_shoppingcategory",
    "change_shoppingcategory",
    "delete_shoppingcategory",
    "change_itemexpiry",
    "delete_itemexpiry",
    "edit_shoppinglist",
    "delete_shoppinglist",
    "add_shopitems",
    "change_shopitems",
    "delete_shopitems",
    "change_family",
    "delete_family",
]

PERMISSION_LABELS = {
    "add_food_items": "Add Food Item",
    "change_food_items": "Edit Food Item",
    "delete_food_items": "Delete Food Item",
    "add_other_items": "Add Other Item",
    "change_other_items": "Edit Other Item",
    "delete_other_items": "Delete Other Item",
    "add_shopping_list": "Add Shopping List",
    "view_profile_detail": "View Profile Detail",
    "edit_members": "Edit Members",
    "change_category": "Edit Category",
    "add_category": "Add Category",
    "delete_category": "Delete Category",
    "add_shoppingcategory": "Add Shopping Category",
    "change_shoppingcategory": "Edit Shopping Category",
    "delete_shoppingcategory": "Delete Shopping Category",
    "change_itemexpiry": "Change Item Expiry",
    "delete_itemexpiry": "Delete Item Expiry",
    "edit_shoppinglist": "Edit Shopping List",
    "delete_shoppinglist": "Delete Shopping List",
    "add_shopitems": "Add Shop Item",
    "change_shopitems": "Edit Shop Item",
    "delete_shopitems": "Delete Shop Item",
    "change_family": "Change Family",
    "delete_family": "Delete Family",
}


class EditUserPermissionsForm(forms.Form):
    role = forms.ChoiceField(
        choices=Profile.Role.choices,
        label="Role",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.filter(codename__in=CODENAMES),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Custom Permissions",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["permissions"].label_from_instance = (
            lambda obj: PERMISSION_LABELS.get(obj.codename, str(obj))
        )
