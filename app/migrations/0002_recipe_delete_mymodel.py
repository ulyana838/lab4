# Generated by Django 5.1.2 on 2024-10-20 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('ingredients', models.TextField()),
                ('instructions', models.TextField()),
            ],
        ),
        migrations.DeleteModel(
            name='MyModel',
        ),
    ]
