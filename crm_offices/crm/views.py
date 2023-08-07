from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import sys
from .forms import *
from django.contrib import messages
from crm_offices.settings import logger
from .models import *
from datetime import datetime, date
from crm_offices.utils import get_office, get_year, months, months_to_digit
from django.views.generic.edit import FormMixin
from calendar import monthrange
import copy
import json
import pandas as pd
from django.contrib.auth.mixins import UserPassesTestMixin
from transliterate import slugify


class StaffMemberRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


@login_required
def index(request):
    context = {
        'title': 'Сводная таблица по пунктам'
    }
    # return render(request, 'crm/home.html', context)
    logger.info(f'REQUEST SESSION {request.session.__dict__}')
    current_year = datetime.today().year
    expenses = Expenses.objects.filter(date__year=current_year)
    fines = Fines.objects.filter(date__year=current_year)
    salaries = Salaries.objects.filter(date__year=current_year)
    results = []
    for i in expenses:
        results.append({
            'date': i.date,
            'amount': i.amount,
            'currency': i.currency.name,
            'category': i.expense_type.name,
            'office': i.office.name
        })
    for i in fines:
        results.append({
            'date': i.date,
            'amount': i.amount * -1,
            'currency': 'Сум',
            'category': 'Штрафы',
            'office': i.employee.office.name
        })
    for i in salaries:
        results.append({
            'date': i.date,
            'amount': i.amount,
            'currency': 'Сум',
            'category': 'Зарплата',
            'office': i.employee.office.name
        })
    logger.info(f'RESULTS - {results}')
    with open('expenses.json', 'w') as file:
        json.dump(results, file, indent=4, default=str)
    if results:
        df = pd.DataFrame.from_dict(results)
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = pd.DatetimeIndex(df['date']).month
        group_data = df.groupby(['month', 'office', 'currency'], as_index=False)['amount'].sum()
        columns = ['Пункт']
        for i in range(1, 13):
            columns.extend([f'{i} (Сум)', f'{i} ($)'])
        result_df = pd.DataFrame(columns=columns)
        for i in df['office'].unique():
            result_df.loc[len(result_df.index)] = [i, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                                   0]
        result_df = result_df.set_index('Пункт')
        for i, row in group_data.iterrows():
            month = row['month']
            if row["currency"] == 'Доллар США':
                currency = ' ($)'
            elif row["currency"] == 'Сум':
                currency = ' (Сум)'
            office = row['office']
            amount = row['amount']
            result_df.loc[office, f'{month}{currency}'] = amount
        result_df['Итого (Сум)'] = result_df[[i for i in result_df.columns if '(Сум)' in i]].sum(1)
        result_df['Итого ($)'] = result_df[[i for i in result_df.columns if '($)' in i]].sum(1)
        result_df.loc['Итого', :] = result_df.sum(axis=0)
        result_df = result_df.reset_index()
        for i in result_df.columns[1:]:
            result_df[i] = result_df[i].astype(int)
        result_table = result_df.values.tolist()
    else:
        result_table = None
    context['result_table'] = result_table
    context['months'] = [i for i in months.values()]
    return render(request, 'crm/home.html', context)


def activate_year(request, year):
    request.session['year'] = year
    last_page = request.META.get("HTTP_REFERER")
    logger.info(f'LAST PAGE - {last_page}')
    return redirect(last_page)


def login_page(request):
    login_form = UserLoginForm()
    register_form = UserRegisterForm()
    context = {
        'login_form': login_form,
        'register_form': register_form
    }
    return render(request, 'crm/login.html', context)


def user_login(request):
    if request.method == 'POST' and 'login-button' in request.POST:
        login_form = UserLoginForm(data=request.POST)
        # register_form = UserRegisterForm()
        if login_form.is_valid():
            user = login_form.get_user()
            login(request, user)
            messages.success(request, 'Вход выполнен')
        else:
            register_form = UserRegisterForm()
            messages.error(request, 'Вход не выполнен, проверьте форму')
            return render(request, 'crm/login.html', {'login_form': login_form, 'register_form': register_form})
    if request.user.is_superuser:
        return redirect('home')
    else:
        if Offices.objects.filter(admin_user=request.user):
            first_office = Offices.objects.filter(admin_user=request.user).first()
            return redirect('offices', slug=first_office.slug)
        else:
            return redirect('home')

def user_register(request):
    if request.method == 'POST' and 'register-button' in request.POST:
        register_form = UserRegisterForm(data=request.POST)
        if register_form.is_valid():
            user = register_form.save()
            login(request, user)
            messages.success(request, 'Вы успешно зарегистрировались. После модерации Вы получите доступ к функционалу')
        else:
            login_form = UserLoginForm()
            messages.error(request, 'Вы не зарегистрировались. Проверьте форму')
            return render(request, 'crm/login.html', {'login_form': login_form, 'register_form': register_form})
    return redirect('home')


def user_logout(request):
    logout(request)
    messages.success(request, 'Вы вышли из аккаунта')
    return redirect('home')


def office_page(request, slug):
    request.session['office'] = slug
    logger.info(f'REQUEST {request.path}')
    office = Offices.objects.get(slug=slug)
    if office.admin_user != request.user and not request.user.is_superuser:
        return redirect('home')
    context = {
        'title': office.name
    }
    current_year = get_year(request.session)
    expenses = Expenses.objects.filter(date__year=current_year, office=office)
    fines = Fines.objects.filter(date__year=current_year, employee__office=office)
    salaries = Salaries.objects.filter(date__year=current_year, employee__office=office)
    results = []
    for i in expenses:
        results.append({
            'date': i.date,
            'amount': i.amount,
            'currency': i.currency.name,
            'category': i.expense_type.name
        })
    for i in fines:
        results.append({
            'date': i.date,
            'amount': i.amount * -1,
            'currency': 'Сум',
            'category': 'Штрафы'
        })
    for i in salaries:
        results.append({
            'date': i.date,
            'amount': i.amount,
            'currency': 'Сум',
            'category': 'Зарплата'
        })
    logger.info(f'RESULTS - {results}')
    with open('expenses.json', 'w') as file:
        json.dump(results, file, indent=4, default=str)
    if results:
        df = pd.DataFrame.from_dict(results)
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = pd.DatetimeIndex(df['date']).month
        group_data = df.groupby(['month', 'category', 'currency'], as_index=False)['amount'].sum()
        columns = ['Месяц', 'Аренда (Сум)', 'Аренда ($)', 'Коммунальные платежи', 'Иные расходы', 'Зарплата', 'Штрафы']
        result_df = pd.DataFrame(columns=columns)
        for i in range(1, 13):
            result_df.loc[len(result_df.index)] = [i, 0, 0, 0, 0, 0, 0]
        result_df = result_df.set_index('Месяц')
        for i, row in group_data.iterrows():
            month = row['month']
            if row["category"] == 'Аренда' and row["currency"] == 'Доллар США':
                category = 'Аренда ($)'
            elif row["category"] == 'Аренда' and row["currency"] == 'Сум':
                category = 'Аренда (Сум)'
            else:
                category = row["category"]
            amount = row['amount']
            result_df.loc[month, category] = amount
        result_df['Итого (Сум)'] = result_df[
            ['Аренда (Сум)', 'Коммунальные платежи', 'Иные расходы', 'Зарплата', 'Штрафы']].sum(1)
        result_df['Итого ($)'] = result_df[['Аренда ($)']].sum(1)
        result_df.loc['Итого за год', :] = result_df.sum(axis=0)
        result_df = result_df.reset_index()
        result_df['Месяц'][:12] = result_df['Месяц'][:12].apply(lambda x: months[int(x)])
        for i in result_df.columns[1:]:
            result_df[i] = result_df[i].astype(int)
        result_table = result_df.values.tolist()
    else:
        result_table = None
    context['result_table'] = result_table
    return render(request, 'crm/office.html', context)


def get_expenses(office, year, expense_type):
    all_payments = Expenses.objects.filter(office__slug=office, expense_type__name=expense_type)
    if expense_type in ['Аренда', 'Коммунальные платежи', 'Иные расходы']:
        years_of_payments = [i.year for i in all_payments.dates('period', 'year')]
    result_payments = all_payments.filter(period__year=year)
    logger.info(f'ALL PAYMENTS - {all_payments}, YEARS - {years_of_payments}, '
                f'RESULT_PAYMENTS - {result_payments}')
    result_table = {}
    for key, value in months.items():
        result = []
        for payment in result_payments:
            if payment.period.month == key:
                result.append(payment)
        result_table[value] = result
    logger.info(f'RESULT TABLE - {result_table}')
    return result_table


def rent_page(request):
    context = {
        'title': 'Расходы по аренде'
    }
    current_office = get_office(request.session)
    office = Offices.objects.get(slug=current_office)
    if office.admin_user != request.user and not request.user.is_superuser:
        return redirect('home')
    current_year = get_year(request.session)
    if request.method == 'POST':
        post = request.POST.copy()
        post['period'] = f'01.{months_to_digit[post["period"]]}.{str(current_year)}'
        request.POST = post
        form = AddRentPaymentForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            logger.info(f'FORM DATA - {form_data}')
            new_rent_payment = Expenses.objects.create(
                date=form_data['date'],
                period=form_data['period'],
                amount=form_data['amount'],
                currency=Currency.objects.get(id=form_data['currency']),
                office=Offices.objects.get(slug=current_office),
                expense_type=ExpensesTypes.objects.get(name='Аренда'),
            )
            logger.info(f'NEW EXPENSE WAS CREATED - {new_rent_payment}')
            messages.success(request, 'Новый платеж по аренде добавлен')
        else:
            logger.info(f'FORM ERRORS - {form.errors}')
            context['form'] = form
            messages.error(request, 'Допущена ошибка. Проверьте форму')
            return render(request, 'crm/rent_page.html', context)
    context['result_table'] = get_expenses(current_office, current_year, 'Аренда')
    context['form'] = AddRentPaymentForm()
    return render(request, 'crm/rent_page.html', context)


def expenses_page(request):
    logger.info(f'REQUEST {request.path}')
    if request.path == '/public_services/':
        data = {
            'title': 'Коммунальные платежи',
            'name': 'Коммунальные платежи',
            'singular_name': 'коммунальный платеж'
        }
    elif request.path == '/other_expenses/':
        data = {
            'title': 'Иные расходы',
            'name': 'Иные расходы',
            'singular_name': 'иной платеж'
        }
    context = {
        'title': data["title"]
    }
    current_office = get_office(request.session)
    office = Offices.objects.get(slug=current_office)
    if office.admin_user != request.user and not request.user.is_superuser:
        return redirect('home')
    current_year = get_year(request.session)
    if request.method == 'POST':
        post = request.POST.copy()
        logger.info(f'POST  - {post}')
        request.POST = post
        form = AddExpenseForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            logger.info(f'FORM DATA - {form_data}')
            new_rent_payment = Expenses.objects.create(
                date=form_data['date'],
                period=form_data['date'],
                amount=form_data['amount'],
                currency=Currency.objects.get(id=1),
                office=Offices.objects.get(slug=current_office),
                expense_type=ExpensesTypes.objects.get(name=data["name"]),
                comment=form_data['comment']
            )
            logger.info(f'NEW EXPENSE WAS CREATED - {new_rent_payment}')
            messages.success(request, f'Новый {data["singular_name"]} добавлен')
        else:
            logger.info(f'FORM ERRORS - {form.errors}')
            context['form'] = form
            messages.error(request, 'Допущена ошибка. Проверьте форму')
            return render(request, 'crm/expenses_page.html', context)
    context['result_table'] = get_expenses(current_office, current_year, data["name"])
    context['form'] = AddExpenseForm()
    return render(request, 'crm/expenses_page.html', context)


def fines_page(request):
    context = {
        'title': 'Штрафы'
    }
    current_office = get_office(request.session)
    office = Offices.objects.get(slug=current_office)
    if office.admin_user != request.user and not request.user.is_superuser:
        return redirect('home')
    current_year = get_year(request.session)
    current_employees = Employees.objects.filter(office=Offices.objects.get(slug=current_office)).order_by('name')
    employees_choices = [(i.id, i.name) for i in current_employees]
    if request.method == 'POST':
        post = request.POST.copy()
        logger.info(f'POST  - {post}')
        request.POST = post
        form = AddFineForm(request.POST, employees_choices=employees_choices)
        if form.is_valid():
            form_data = form.cleaned_data
            logger.info(f'FORM DATA - {form_data}')
            new_fine = Fines.objects.create(
                date=form_data['date'],
                amount=form_data['amount'],
                employee=form_data['employee'],
                comment=form_data['comment']
            )
            logger.info(f'NEW EXPENSE WAS CREATED - {new_fine}')
            messages.success(request, f'Новый штраф добавлен')
        else:
            logger.info(f'FORM ERRORS - {form.errors}')
            context['form'] = form
            messages.error(request, 'Допущена ошибка. Проверьте форму')
            return render(request, 'crm/expenses_page.html', context)

    full_all_fines = Fines.objects.filter(employee__in=current_employees).order_by('date')
    logger.info(f'FULL ALL FINES - {full_all_fines}')
    all_fines = full_all_fines.filter(date__year=current_year)
    logger.info(f'ALL FINES - {all_fines}')
    result_dict = {}
    for month_number, month_name in months.items():
        days = monthrange(current_year, month_number)
        weekdays = []
        all_days = []
        for day in range(1, days[1] + 1):
            weekdays.append(date(current_year, month_number, day).weekday())
            all_days.append(day)
        employees_rows = {}
        for employee in current_employees:
            employees_rows[employee.id] = [employee.name] + [['-', '-'][:]] * days[1]
            logger.info(f'employees_rows - {employees_rows[employee.id]}')
        result_month = {'weekdays': weekdays, 'all_days': all_days, 'employees_rows': employees_rows, 'month_number': month_number}
        result_dict[month_name] = result_month
        logger.info(f'{month_name} - {weekdays} / {all_days}')
    for fine in all_fines:
        fine_month = fine.date.month
        fine_day = fine.date.day
        fine_employee = fine.employee
        current_fine_data = result_dict[months[fine_month]]['employees_rows'][fine_employee.id][fine_day][1]
        if current_fine_data != '-':
            new_fine_data = current_fine_data + '<br />' + f'{fine.amount} / {fine.comment}'
        else:
            new_fine_data = f'{fine.amount} / {fine.comment}'
        result_dict[months[fine_month]]['employees_rows'][fine_employee.id][fine_day] = ['*', new_fine_data]
        logger.info(f'{result_dict[months[fine_month]]["employees_rows"][fine_employee.id]}')
    today_date = date.today()
    today = {
        'year': today_date.year,
        'month': today_date.month - 1,
        'day': today_date.day
    }
    context['today'] = today
    context['result_dict'] = result_dict
    context['results'] = Fines.objects.filter(date__year=current_year, employee__office=Offices.objects.get(slug=current_office))
    context['form'] = AddFineForm(
        employees_choices=employees_choices
        )
    context['year'] = current_year
    context['all_fines'] = all_fines
    return render(request, 'crm/fines_page.html', context)


def salary_page(request):
    context = {
        'title': 'Зарплата'
    }
    current_office = get_office(request.session)
    office = Offices.objects.get(slug=current_office)
    if office.admin_user != request.user and not request.user.is_superuser:
        return redirect('home')
    current_year = get_year(request.session)
    current_employees = Employees.objects.filter(office=Offices.objects.get(slug=current_office)).order_by('name')
    employees_choices = [(i.id, i.name) for i in current_employees]
    if request.method == 'POST' and 'single-date-button' in request.POST:
        post = request.POST.copy()
        logger.info(f'POST  - {post}')
        request.POST = post
        form = AddSalaryForm(request.POST, employees_choices=employees_choices)
        if form.is_valid():
            form_data = form.cleaned_data
            logger.info(f'FORM DATA - {form_data}')
            new_fine = Salaries.objects.create(
                date=form_data['date'],
                amount=form_data['amount'],
                employee=form_data['employee'],
                comment=form_data['comment']
            )
            logger.info(f'NEW SALARY PAYMENT WAS CREATED - {new_fine}')
            messages.success(request, f'Новая выплата добавлена')
        else:
            logger.info(f'FORM ERRORS - {form.errors}')
            context['form'] = form
            messages.error(request, 'Допущена ошибка. Проверьте форму')
            return render(request, 'crm/expenses_page.html', context)
    if request.method == 'POST' and 'multiple-date-button' in request.POST:
        post = request.POST.copy()
        logger.info(f'POST  - {post}')
        request.POST = post
        form = AddSalaryMultipleForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            logger.info(f'FORM DATA - {form_data}')
            for employee_id, date_list in form_data['date_employee'].items():
                employee = Employees.objects.get(id=employee_id)
                for date_dict in date_list:
                    salary_date = date(int(date_dict['year']), int(date_dict['month']), int(date_dict['day']))
                    new_fine = Salaries.objects.create(
                        date=salary_date,
                        amount=form_data['amount'],
                        employee=employee,
                        comment=form_data['comment']
                    )
                    logger.info(f'NEW SALARY PAYMENT WAS CREATED - {new_fine}')
            messages.success(request, f'Новые выплаты добавлены')
        else:
            logger.info(f'FORM ERRORS - {form.errors}')
            context['form'] = form
            messages.error(request, 'Допущена ошибка. Проверьте форму')
            return render(request, 'otk/schedule_page.html', context)
    full_all_fines = Fines.objects.filter(employee__in=current_employees).order_by('date')
    logger.info(f'FULL ALL FINES - {full_all_fines}')
    all_fines = full_all_fines.filter(date__year=current_year)
    logger.info(f'ALL FINES - {all_fines}')
    full_all_salary = Salaries.objects.filter(employee__in=current_employees).order_by('date')
    logger.info(f'FULL ALL SALARY - {full_all_salary}')
    all_salary = full_all_salary.filter(date__year=current_year)
    logger.info(f'ALL SALARY - {all_salary}')
    result_dict = {}
    for month_number, month_name in months.items():
        days = monthrange(current_year, month_number)
        weekdays = []
        all_days = []
        for day in range(1, days[1] + 1):
            weekdays.append(date(current_year, month_number, day).weekday())
            all_days.append(day)
        employees_rows = {}
        for employee in current_employees:
            employees_rows[employee.id] = [employee] + [['-', {'fines': [], 'salary': []}][:]] * days[1]
            employees_rows[employee.id].extend([0, 0])
            logger.info(f'employees_rows - {employees_rows[employee.id]}')
        result_month = {'weekdays': weekdays, 'all_days': all_days, 'employees_rows': employees_rows,
                        'month_number': month_number}
        result_dict[month_name] = result_month
        logger.info(f'{month_name} - {weekdays} / {all_days}')
    for fine in all_fines:
        fine_month = fine.date.month
        fine_day = fine.date.day
        fine_employee = fine.employee
        new_fine_data = copy.deepcopy(result_dict[months[fine_month]]['employees_rows'][fine_employee.id][fine_day][1])
        logger.info(f'CURR FINE DATA = {new_fine_data}')
        new_fine_data['fines'].append(f'{fine.amount} / {fine.comment}')

        # if new_fine_data['fines']:
        #     new_fine_data['fines'].append(f'{fine.amount} / {fine.comment}')
        # else:
        #     new_fine_data = current_fine_data
        #     new_fine_data['fines']
        result_dict[months[fine_month]]['employees_rows'][fine_employee.id][fine_day] = ['*', new_fine_data]
        result_dict[months[fine_month]]['employees_rows'][fine_employee.id][-1] += fine.amount
        logger.info(f'{result_dict[months[fine_month]]["employees_rows"][fine_employee.id]}')
    for salary in all_salary:
        salary_month = salary.date.month
        salary_day = salary.date.day
        salary_employee = salary.employee
        current_salary_label, new_salary_data = copy.deepcopy(result_dict[months[salary_month]]['employees_rows'][salary_employee.id][salary_day])
        new_salary_data['salary'].append(f'{salary.amount} / {salary.comment}')
        # if current_salary_data != '-':
        #     new_salary_data = current_salary_data['salary'].append(f'{salary.amount} / {salary.comment}')
        # else:
        #     new_salary_data = {'salary': [f'{salary.amount} / {salary.comment}']}
        if current_salary_label not in ['-', '$', '* $']:
            new_salary_label = current_salary_label + ' $'
        elif current_salary_label == '* $':
            new_salary_label = current_salary_label
            logger.info('not change')
        else:
            new_salary_label = '$'
        result_dict[months[salary_month]]['employees_rows'][salary_employee.id][salary_day] = [new_salary_label, new_salary_data]
        result_dict[months[salary_month]]['employees_rows'][salary_employee.id][-2] += salary.amount
        logger.info(f'{result_dict[months[salary_month]]["employees_rows"][salary_employee.id]}')
    today_date = date.today()
    today = {
        'year': today_date.year,
        'month': today_date.month - 1,
        'day': today_date.day
    }
    context['today'] = today
    context['result_dict'] = result_dict
    context['results'] = Fines.objects.filter(date__year=current_year,
                                              employee__office=Offices.objects.get(slug=current_office))
    context['form'] = AddSalaryForm(
        employees_choices=employees_choices
    )
    context['form_multiple'] = AddSalaryMultipleForm()
    context['year'] = current_year
    context['all_fines'] = all_fines
    return render(request, 'crm/salary_page.html', context)


class OfficesList(StaffMemberRequiredMixin, FormMixin, ListView):
    model = Offices
    form_class = AddOfficeForm
    paginate_by = 20
    template_name = 'crm/offices_list.html'
    context_object_name = 'offices'
    ordering = 'id'
    success_url = '/offices/'

    # def get_success_url(self, **kwargs):
    #     return redirect('offices_list')

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        logger.info(f'Form {form}')
        data = form.cleaned_data
        logger.info(f'data {data}')
        name = data['name']
        slug = slugify(name, language_code='ru')
        if slug in [i.slug for i in Offices.objects.all()]:
            slug += f'-{str(Offices.objects.all().order_by("id").last().id) + "1"}'
        logger.info(f'SLUG - {slug}')
        data['slug'] = slug
        self.object = Offices.objects.create(**data)
        self.object.save()
        messages.success(self.request, f'Пункт добавлен')
        return HttpResponseRedirect(self.get_success_url())
        # return JsonResponse({'error': False, 'message': 'Комментарий добавлен'})

    def form_invalid(self, form):
        logger.info(f'FORM ERRORS - {type(form.errors)}')
        messages.error(self.request, f'Пункт не добавлен. Ошибка в форме\n{form.errors}')
        return redirect('offices_list')
        # return JsonResponse({'error': True, 'errors': form.errors, 'message': 'Проверьте форму'})


class EmployeesList(FormMixin, ListView):
    model = Employees
    form_class = AddEmployeeForm
    paginate_by = 20  # if pagination is desired
    template_name = 'crm/employees_list.html'
    context_object_name = 'employees'
    ordering = 'id'

    def get_queryset(self):
        current_office = get_office(self.request.session)
        return Employees.objects.filter(office__slug=current_office)

    def get_initial(self):
        current_office = get_office(self.request.session)
        logger.info(f'CURRENT OFFICE - {current_office}')
        return {'office': Offices.objects.get(slug=current_office)}

    def get_success_url(self, **kwargs):
        return reverse_lazy('employees')

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        messages.success(self.request, f'Сотрудник добавлен')
        return HttpResponseRedirect(self.get_success_url())
        # return JsonResponse({'error': False, 'message': 'Комментарий добавлен'})

    def form_invalid(self, form):
        messages.error(self.request, f'Сотрудник не добавлен. Ошибка в форме')
        return JsonResponse({'error': True, 'errors': form.errors, 'message': 'Проверьте форму'})


