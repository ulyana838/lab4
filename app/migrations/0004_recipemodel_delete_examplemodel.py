# Generated by Django 5.1.2 on 2024-10-22 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_examplemodel_delete_recipe'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecipeModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('ingredients', models.TextField()),
                ('instructions', models.TextField()),
                ('cooking_time', models.PositiveIntegerField()),
            ],
        ),
        migrations.DeleteModel(
            name='ExampleModel',
        ),
    ]
