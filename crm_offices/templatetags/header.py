from django import template
from crm.models import Offices, Expenses
# from crm_offices.utils import safe_get
from crm_offices.settings import logger

register = template.Library()


@register.inclusion_tag('offices_tpl.html')
def get_offices(request):
    offices = Offices.objects.all()
    logger.info(f'PATH - {request.path}')
    current_year = int(request.path[1:].split('/')[0])
    #TODO передать slug для определения активной ссылки
    return {'offices': offices, 'request': request, 'year': current_year}


@register.inclusion_tag('years_buttons_tpl.html')
def get_years_buttons(request):
    logger.info(f'PATH - {request.path}')
    current_year = int(request.path[1:].split('/')[0])
    logger.info(f'CURRENT YEAR - {current_year}')
    first_expense = Expenses.objects.all().order_by('date').first
    logger.info(f'FIRST EXPENSE - {first_expense}')
    logger.info(f'REQUEST GET COPY - {request.GET.copy()}')
    years = range(current_year, current_year + 5)
    return {'years': years}