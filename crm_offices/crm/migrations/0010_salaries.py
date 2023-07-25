# Generated by Django 4.2.3 on 2023-07-25 12:34

import crm_offices.utils
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0009_alter_offices_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='Salaries',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Дата выплаты')),
                ('amount', models.IntegerField(verbose_name='Сумма выплаты')),
                ('comment', models.TextField(verbose_name='Комментарий')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='salaries', to='crm.employees', verbose_name='Сотрудник')),
            ],
            options={
                'verbose_name': 'Зарплата',
                'verbose_name_plural': 'Зарплаты',
            },
            bases=(crm_offices.utils.CustomStr, models.Model),
        ),
    ]