# Generated by Django 4.2.3 on 2023-07-19 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0006_alter_expenses_currency'),
    ]

    operations = [
        migrations.AddField(
            model_name='expenses',
            name='period',
            field=models.DateField(default='2023-01-01', verbose_name='Оплата за месяц'),
            preserve_default=False,
        ),
    ]
