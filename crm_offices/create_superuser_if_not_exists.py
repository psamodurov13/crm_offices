import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crm_offices.settings")
django.setup()

from django.contrib.auth.models import User
from crm.models import *

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')

if not Currency.objects.all():
    currencies = [
        ['Сум', 'Soʻm'],
        ['Доллар США', '$']
    ]
    for i in currencies:
        Currency.objects.create(
            name=i[0],
            symbol=i[1]
        )


if not ExpensesTypes.objects.all():
    expenses_types = ['Аренда', 'Иные расходы', 'Коммунальные платежи', 'Зарплата']
    for i in expenses_types:
        ExpensesTypes.objects.create(
            name=i
        )