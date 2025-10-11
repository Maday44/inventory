from django import forms
from .models import FoodItem  # import your model name exactly

class FoodForm(forms.ModelForm):
    class Meta:
        model = FoodItem  # make sure this matches your model
        fields = ['title', 'brand', 'quantity', 'exp_date', 'image']  # adjust fields as needed
