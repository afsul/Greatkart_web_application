# Generated by Django 3.1 on 2022-03-25 10:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0003_cartitem_variations'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='variations',
        ),
    ]
