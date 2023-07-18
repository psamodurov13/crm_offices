from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .forms import UserLoginForm
from django.contrib import messages
from crm_offices.settings import logger
from .models import *
from datetime import datetime


@login_required
def index(request):
    context = {
        'title': 'Home page'
    }
    # return render(request, 'crm/home.html', context)
    current_year = datetime.today().year
    return redirect('year_page', current_year)


def year_page(request, year):
    context = {
        'title': f'Home page {year}',
        'year': year
    }
    return render(request, 'crm/year_page.html', context)



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


def office(request, year, slug):
    logger.info(f'REQUEST {request.path}')
    office = Offices.objects.get(slug=slug)
    context = {
        'title': office.name
    }
    return render(request, 'crm/office.html', context)