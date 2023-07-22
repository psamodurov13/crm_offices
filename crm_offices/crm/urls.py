from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('rent/', views.rent_page, name='rent'),
    path('salary/', views.rent_page, name='salary'),
    path('other_expenses/', views.expenses_page, name='other_expenses'),
    path('public_services/', views.expenses_page, name='public_services'),
    path('fines/', views.fines_page, name='fines'),
    path('employees/', views.EmployeesList.as_view(), name='employees'),
    path('<int:year>/', views.activate_year, name='activate_year'),
    path('offices/', views.OfficesList.as_view(), name='offices_list'),
    path('offices/<str:slug>', views.office_page, name='offices'),
    path('login_page', views.login_page, name='login_page'),
    path('login', views.user_login, name='login'),
    path('logout', views.user_logout, name='logout'),
]
