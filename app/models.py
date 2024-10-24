from django.db import models

class RecipeModel(models.Model):
    name = models.CharField(max_length=100)
    ingredients = models.TextField()
    instructions = models.TextField()
    cooking_time = models.PositiveIntegerField()

    def __str__(self):
        return self.name