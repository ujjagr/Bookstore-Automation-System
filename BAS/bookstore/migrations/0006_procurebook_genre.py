# Generated by Django 5.0.3 on 2024-03-17 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookstore', '0005_delete_buyer_alter_sales_book'),
    ]

    operations = [
        migrations.AddField(
            model_name='procurebook',
            name='genre',
            field=models.CharField(default='', max_length=50),
        ),
    ]
