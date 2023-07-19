from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .forms import UserLoginForm
from django.contrib import messages
from crm_offices.settings import logger
from .models import *
from datetime import datetime
from crm_offices.utils import get_office, get_year


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


def rent_page(request):
    context = {
        'title': 'Rent page'
    }
    current_office = get_office(request.session)
    current_year = get_year(request.session)
    all_rent_payments = Expenses.objects.filter(office__slug=current_office)
    years_of_payments = [i.year for i in all_rent_payments.dates('date', 'year')]
    result_payments = all_rent_payments.filter(date__year=current_year)
    logger.info(f'RENT PAYMENTS - {all_rent_payments}, YEARS - {years_of_payments}, RESULT_PAYMENTS - {result_payments}')
    return render(request, 'crm/rent_page.html', context)