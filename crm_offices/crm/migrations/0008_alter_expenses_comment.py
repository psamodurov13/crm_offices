# Generated by Django 4.2.3 on 2023-07-19 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0007_expenses_period'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expenses',
            name='comment',
            field=models.TextField(blank=True, verbose_name='Комментарий'),
        ),
    ]
