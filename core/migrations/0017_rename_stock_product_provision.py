# Generated by Django 5.2.1 on 2025-06-01 15:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_rename_minimum_stock_product_stock'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='stock',
            new_name='provision',
        ),
    ]
