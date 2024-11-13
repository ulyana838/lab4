from django import forms  # Импорт модуля forms из Django для создания форм
from .models import RecipeModel  # Импорт модели RecipeModel из текущего приложения

class RecipeForm(forms.ModelForm):  # Определение класса формы, наследующего от forms.ModelForm
    class Meta:  # Вложенный класс Meta для настройки формы
        model = RecipeModel  # Указание модели, на основе которой создается форма
        fields = ['name', 'ingredients', 'instructions', 'cooking_time']  # Список полей модели, которые будут включены в форму
        labels = {
            'name': 'Название блюда',
            'ingredients': 'Ингредиенты',
            'instructions': 'Инструкция',
            'cooking_time': 'Время приготовления (минуты)',
        }
