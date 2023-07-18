from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('<int:year>/', views.year_page, name='year_page'),
    path('<int:year>/offices/<str:slug>', views.office, name='offices'),
    path('login_page', views.login_page, name='login_page'),
    path('login', views.user_login, name='login'),
    path('logout', views.user_logout, name='logout'),
]
