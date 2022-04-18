# Generated by Django 3.1 on 2022-03-27 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_auto_20220326_1017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('New', 'New'), ('Accepted', 'Accepted'), ('Order Shipped', 'Order Shipped'), ('Order Out for Delivery', 'Order Out for Delivery'), ('Order Delivered', 'Order Delivered'), ('Return', 'Return'), ('Return collected', 'Return collected'), ('Cancelled', 'Cancelled')], default='New', max_length=50),
        ),
    ]