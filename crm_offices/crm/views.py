from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .forms import UserLoginForm, AddRentPaymentForm, AddExpenseForm, AddEmployeeForm, AddOfficeForm, AddFineForm
from django.contrib import messages
from crm_offices.settings import logger
from .models import *
from datetime import datetime, date
from crm_offices.utils import get_office, get_year, months, months_to_digit
from django.views.generic.edit import FormMixin
from calendar import monthrange


@login_required
def index(request):
    context = {
        'title': 'Home page'
    }
    # return render(request, 'crm/home.html', context)
    logger.info(f'REQUEST SESSION {request.session.__dict__}')
    current_year = datetime.today().year
    return render(request, 'crm/home.html', context)


def activate_year(request, year):
    request.session['year'] = year
    last_page = request.META.get("HTTP_REFERER")
    logger.info(f'LAST PAGE - {last_page}')
    return redirect(last_page)


def login_page(request):
    login_form = UserLoginForm()
    context = {
        'login_form': login_form,
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
            messages.error(request, 'Вход не выполнен, проверьте форму')
            return render(request, 'crm/login.html', {'login_form': login_form})
    return redirect('home')


def user_logout(request):
    logout(request)
    messages.success(request, 'Вы вышли из аккаунта')
    return redirect('home')


def office_page(request, slug):
    request.session['office'] = slug
    logger.info(f'REQUEST {request.path}')
    office = Offices.objects.get(slug=slug)
    context = {
        'title': office.name
    }
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
        'title': 'Rent page'
    }
    current_office = get_office(request.session)
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
            'title': 'Public Services',
            'name': 'Коммунальные платежи',
            'singular_name': 'коммунальный платеж'
        }
    elif request.path == '/other_expenses/':
        data = {
            'title': 'Other Expenses',
            'name': 'Иные расходы',
            'singular_name': 'иной платеж'
        }
    context = {
        'title': data["title"]
    }
    current_office = get_office(request.session)
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

    # context['result_table'] = get_expenses(current_office, current_year, data["name"])
    #TODO сделать словарь со штрафами для каждого сотрудника и вывести их на странице в виде аккордеона
    #TODO в форму передавать только сотрудников выбранного оффиса

    all_fines = Fines.objects.filter(employee__in=current_employees).order_by('date')
    result_dict = {}
    for month_number, month_name in months.items():
        days = monthrange(current_year, month_number)
        first_day = days[0]
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


class OfficesList(FormMixin, ListView):
    model = Offices
    form_class = AddOfficeForm
    paginate_by = 20
    template_name = 'crm/offices_list.html'
    context_object_name = 'offices'
    ordering = 'id'

    def get_success_url(self, **kwargs):
        return redirect('offices_list')

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save(commit=False)
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


