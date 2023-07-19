from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('rent/', views.rent_page, name='rent'),
    path('salary/', views.rent_page, name='salary'),
    path('other_expenses/', views.rent_page, name='other_expenses'),
    path('public_services/', views.rent_page, name='public_services'),
    path('fines/', views.rent_page, name='fines'),
    path('employees/', views.rent_page, name='employees'),
    path('<int:year>/', views.activate_year, name='activate_year'),
    path('offices/<str:slug>', views.office_page, name='offices'),
    path('login_page', views.login_page, name='login_page'),
    path('login', views.user_login, name='login'),
    path('logout', views.user_logout, name='logout'),
]
