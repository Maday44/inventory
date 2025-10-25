from django import forms
from .models import * 

class FoodForm(forms.ModelForm):
    class Meta:
        model = Food_items
        fields = ['title', 'brand', 'quantity', 'exp_date', 'image']
        widgets = {
            'exp_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        labels = {
            'title': 'Name',
            'brand': 'Brand',
            'quantity': 'Amount / Quantity',
            'exp_date': 'Expiry Date',
            'image': 'Upload Image',
        }

        
class OtherForm(forms.ModelForm):
    class Meta:
        model = Other_items 
        fields = ['title', 'brand', 'quantity', 'image']
        labels = {
            'title': 'Name',
            'brand': 'Brand',
            'quantity': 'Amount / Quantity',
            'image': 'Upload Image',
        }
        