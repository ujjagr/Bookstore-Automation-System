# Generated by Django 5.0.3 on 2024-03-24 19:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookstore', '0016_vendor_list_stock'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='revenue',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
    ]
