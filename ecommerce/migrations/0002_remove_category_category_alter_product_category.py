# Generated by Django 5.1.6 on 2025-03-03 23:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ecommerce", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="category",
            name="category",
        ),
        migrations.AlterField(
            model_name="product",
            name="category",
            field=models.CharField(max_length=50),
        ),
    ]
