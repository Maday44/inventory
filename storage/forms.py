from django import forms
from .models import * 

class FoodForm(forms.ModelForm):
    class Meta:
        model = Food_items
        fields = ['title', 'brand', 'quantity', 'exp_date', 'image']
        
class OtherForm(forms.ModelForm):
    class Meta:
        model = Other_items 
        fields = ['title', 'brand', 'quantity', 'image'] 
        