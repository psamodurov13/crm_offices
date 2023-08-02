import datetime
from django.contrib.auth.models import User
from crm_offices.settings import logger
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import Currency, Employees, Offices, Fines, Salaries


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput())
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput())


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(label="Имя пользователя", widget=forms.TextInput())
    # email = forms.EmailField(label="e-mail", widget=forms.EmailInput())
    password1 = forms.CharField(label="Введите пароль", widget=forms.PasswordInput())
    password2 = forms.CharField(label="Повторите пароль", widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')


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
        fields = ['name', 'address', 'admin_user']

    # def clean(self):
    #     cleaned_data = super().clean()
    #     logger.info(f'CLEAN DATA - {cleaned_data}')
    #     name = cleaned_data['name']
    #     slug = slugify(name)
    #     if slug in [i.slug for i in Offices.objects.all()]:
    #         slug += f'-{str(Offices.objects.all().order_by("id").last() + 1)}'
    #     logger.info(f'SLUG - {slug}')
    #     cleaned_data['slug'] = slug
    #     logger.info(f'FINAL CLEAN DATA - {cleaned_data}')
    #     return cleaned_data


class AddFineForm(forms.ModelForm):
    class Meta:
        model = Fines
        fields = ['date', 'amount', 'employee', 'comment']

    def __init__(self, *args, **kwargs):
        employees_choices = kwargs.pop('employees_choices')
        super().__init__(*args, **kwargs)

        self.fields['employee'] = forms.ChoiceField(
                label='Сотрудник',
                choices=employees_choices, required=True
            )

    def clean(self):
        cleaned_data = super().clean()
        logger.info(f'CLEAN DATA - {cleaned_data}')
        employee_id = cleaned_data['employee']
        cleaned_data['employee'] = Employees.objects.get(id=int(employee_id))
        logger.info(f'FINAL CLEAN DATA - {cleaned_data}')
        return cleaned_data


class AddSalaryForm(forms.ModelForm):
    class Meta:
        model = Salaries
        fields = ['date', 'amount', 'employee', 'comment']

    def __init__(self, *args, **kwargs):
        employees_choices = kwargs.pop('employees_choices')
        super().__init__(*args, **kwargs)

        self.fields['employee'] = forms.ChoiceField(
                label='Сотрудник',
                choices=employees_choices, required=True
            )

    def clean(self):
        cleaned_data = super().clean()
        logger.info(f'CLEAN DATA - {cleaned_data}')
        employee_id = cleaned_data['employee']
        cleaned_data['employee'] = Employees.objects.get(id=int(employee_id))
        logger.info(f'FINAL CLEAN DATA - {cleaned_data}')
        return cleaned_data


class AddSalaryMultipleForm(forms.Form):
    date_employee = forms.JSONField(label='Данные', widget=forms.HiddenInput())
    amount = forms.IntegerField(label='Зарплата', widget=forms.NumberInput())
    comment = forms.Field(label='Комментарий', widget=forms.TextInput())
