from django import template
from crm.models import Offices, Expenses
# from crm_offices.utils import safe_get
from crm_offices.settings import logger
from crm_offices.utils import get_year, get_office

register = template.Library()


@register.inclusion_tag('offices_tpl.html')
def get_offices(request):
    current_office = get_office(request.session)
    offices = Offices.objects.all()
    logger.info(f'PATH - {request.path}')
    return {'offices': offices, 'request': request, 'current_office': current_office}


@register.inclusion_tag('years_buttons_tpl.html')
def get_years_buttons(request):
    current_year = get_year(request.session)
    logger.info(f'YEAR - {current_year}')
    first_expense = Expenses.objects.all().order_by('date').first()
    if first_expense:
        first_year = first_expense.date.year
    else:
        first_year = current_year
    logger.info(f'FIRST EXPENSE - {first_expense}, FIRST DATE - {first_year}')
    years = range(first_year, first_year + 5)
    return {'years': years, 'current_year': current_year}


@register.inclusion_tag('sub_menu_tpl.html')
def get_sub_menu(request):
    menu_dict = {
        'rent': {'path': '/rent/', 'name': 'Аренда'},
        'salary': {'path': '/salary/', 'name': 'Зарплата'},
        'other_expenses': {'path': '/other_expenses/', 'name': 'Иные расходы'},
        'public_services': {'path': '/public_services/', 'name': 'Коммунальные услуги'},
        'fines': {'path': '/fines/', 'name': 'Штрафы'},
        'employees': {'path': '/employees/', 'name': 'Сотрудники'},
    }
    return {'menu_dict': menu_dict, 'request': request}