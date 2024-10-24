from django.db import models  # Импорт модуля models из Django для создания моделей базы данных

class RecipeModel(models.Model):  # Определение класса модели, наследующего от models.Model
    name = models.CharField(max_length=100)  # Поле для хранения названия рецепта, строка длиной до 100 символов
    ingredients = models.TextField()  # Поле для хранения ингредиентов рецепта, текстовое поле
    instructions = models.TextField() 
    cooking_time = models.PositiveIntegerField()  # Поле для хранения времени приготовления рецепта, положительное целое число

    def __str__(self):  # Определение метода __str__ для представления объекта модели в виде строки
        return self.name  # Возвращает название рецепта как строковое представление объекта
