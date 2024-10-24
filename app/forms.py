from django import forms
from .models import RecipeModel

class RecipeForm(forms.ModelForm):
    class Meta:
        model = RecipeModel
        fields = ['name', 'ingredients', 'instructions', 'cooking_time']
