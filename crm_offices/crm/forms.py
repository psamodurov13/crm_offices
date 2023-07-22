import datetime
from crm_offices.settings import logger
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import Currency, Employees, Offices, Fines



class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput())
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput())


class AddRentPaymentForm(forms.Form):
    period = forms.DateField(label='Оплата за период', widget=forms.DateInput())
    date = forms.DateField(label='Дата платежа', widget=forms.DateInput(), initial=datetime.datetime.today())
    amount = forms.IntegerField(label='Сумма', widget=forms.TextInput())
    currency = forms.ChoiceField(
        label='Валюта',
        choices=[(i.id, i.symbol) for i in Currency.objects.all()],
        widget=forms.Select(),
        initial=1
    )


class AddExpenseForm(forms.Form):
    date = forms.DateField(label='Дата платежа', widget=forms.DateInput(), initial=datetime.datetime.today())
    amount = forms.IntegerField(label='Сумма', widget=forms.TextInput())
    comment = forms.Field(label='Комментарий', widget=forms.TextInput())

    # def clean(self):
    #     cleaned_data = self.cleaned_data.copy()
    #     # self.data['period'] = '2023-01-01'
    #     # self.data['period'] = datetime.date(2023, 1, 1)
    #     cleaned_data['comment'] = self.data['comment']
    #     logger.info(f'CLEAN DATA - {self.data} - {self.cleaned_data}')
    #     return cleaned_data

    # def __init__(self, *args, **kwargs):
    #     current_year = kwargs.pop('current_year')
    #     super().__init__(*args, **kwargs)


class AddEmployeeForm(forms.ModelForm):
    class Meta:
        model = Employees
        fields = ['name', 'phone', 'office', 'salary', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 5}),
        }


class AddOfficeForm(forms.ModelForm):
    class Meta:
        model = Offices
        fields = ['name', 'slug', 'address', 'phone', 'admin_user']


class AddFineForm(forms.ModelForm):
    class Meta:
        model = Fines
        fields = ['date', 'amount', 'employee', 'comment']
