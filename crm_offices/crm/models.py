from django.db import models
from crm_offices.utils import CustomStr
from django.contrib.auth.models import User
from django.urls import reverse
from crm_offices.settings import logger


class Offices(CustomStr, models.Model):
    name = models.CharField(verbose_name='Название пункта')
    slug = models.SlugField(verbose_name='URL', unique=True)
    address = models.CharField(verbose_name='Адрес')
    phone = models.CharField(verbose_name='Телефон')
    created_at = models.DateField(verbose_name='Дата добавления', auto_now=True)
    admin_user = models.ForeignKey(User, verbose_name='Администратор пункта', on_delete=models.SET_NULL, null=True,
                                   related_name='office')

    def get_absolute_url(self):
        return reverse('offices', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = 'Пункт'
        verbose_name_plural = 'Пункты'


class Employees(CustomStr, models.Model):
    name = models.CharField(verbose_name='ФИО сотрудника')
    office = models.ForeignKey(Offices, verbose_name='Пункт', on_delete=models.SET_NULL, null=True,
                               related_name='employees')
    phone = models.CharField(verbose_name='Телефон')
    created_at = models.DateField(verbose_name='Дата добавления', auto_now=True)
    salary = models.IntegerField(verbose_name='Зарплата', default=120000)
    comment = models.TextField(verbose_name='Комментарий', blank=True)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'


class Fines(CustomStr, models.Model):
    date = models.DateField(verbose_name='Дата штрафа')
    amount = models.IntegerField(verbose_name='Сумма штрафа')
    employee = models.ForeignKey(Employees, verbose_name='Сотрудник', on_delete=models.CASCADE, related_name='fines')
    comment = models.TextField(verbose_name='Комментарий', blank=True)

    class Meta:
        verbose_name = 'Штраф'
        verbose_name_plural = 'Штрафы'


class Salaries(CustomStr, models.Model):
    date = models.DateField(verbose_name='Дата выплаты')
    amount = models.IntegerField(verbose_name='Сумма выплаты')
    employee = models.ForeignKey(Employees, verbose_name='Сотрудник', on_delete=models.CASCADE, related_name='salaries')
    comment = models.TextField(verbose_name='Комментарий', blank=True)

    class Meta:
        verbose_name = 'Зарплата'
        verbose_name_plural = 'Зарплаты'


class ExpensesTypes(CustomStr, models.Model):
    name = models.CharField(max_length=255, verbose_name='Название типа расхода')

    class Meta:
        verbose_name = 'Тип расхода'
        verbose_name_plural = 'Типы расходов'


class Currency(CustomStr, models.Model):
    name = models.CharField(verbose_name='Валюта')
    symbol = models.CharField(verbose_name='Символ')

    class Meta:
        verbose_name = 'Валюта'
        verbose_name_plural = 'Валюты'


class Expenses(CustomStr, models.Model):
    date = models.DateField(verbose_name='Дата расхода')
    period = models.DateField(verbose_name='Оплата за месяц')
    amount = models.IntegerField(verbose_name='Сумма расхода')
    currency = models.ForeignKey(Currency, default=1,
                                 verbose_name='Валюта', on_delete=models.CASCADE, related_name='expenses')
    office = models.ForeignKey(Offices, verbose_name='Офис', on_delete=models.CASCADE, related_name='expenses')
    expense_type = models.ForeignKey(ExpensesTypes, verbose_name='Тип расхода', on_delete=models.CASCADE,
                                     related_name='expenses')
    comment = models.TextField(verbose_name='Комментарий', blank=True)

    class Meta:
        verbose_name = 'Расход'
        verbose_name_plural = 'Расходы'