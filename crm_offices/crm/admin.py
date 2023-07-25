from django.contrib import admin

from crm_offices.utils import PrePopulatedSlug
from .models import *


class BaseAdmin(admin.ModelAdmin):
    save_as = True
    save_on_top = True


class OfficesAdmin(PrePopulatedSlug, BaseAdmin):
    list_display = ('id', 'name', 'address', 'phone')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'address', 'phone')


class EmployeesAdmin(BaseAdmin):
    list_display = ('id', 'name', 'office', 'phone')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'phone')
    list_filter = ('office',)


class FinesAdmin(BaseAdmin):
    list_display = ('id', 'employee', 'amount', 'comment', 'date')
    list_display_links = ('id', 'employee')
    search_fields = ('comment',)
    list_filter = ('employee',)


class SalariesAdmin(BaseAdmin):
    list_display = ('id', 'employee', 'amount', 'date')
    list_display_links = ('id', 'employee')
    search_fields = ('comment',)
    list_filter = ('employee',)


class ExpensesAdmin(BaseAdmin):
    list_display = ('id', 'amount', 'currency', 'office', 'expense_type', 'date', 'comment')
    list_display_links = ('id', 'amount')
    search_fields = ('comment',)
    list_filter = ('office', 'expense_type',)


class CurrencyAdmin(BaseAdmin):
    list_display = ('id', 'name', 'symbol')
    list_display_links = ('id', 'name')


admin.site.register(Offices, OfficesAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Employees, EmployeesAdmin)
admin.site.register(Fines, FinesAdmin)
admin.site.register(Salaries, SalariesAdmin)
admin.site.register(ExpensesTypes)
admin.site.register(Expenses, ExpensesAdmin)

