from django.urls import path
from . import views
from .views import home, LogoutView, LoginView, filter_data
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', home, name='home'),
    path('login', LoginView.as_view(), name="login"),
    path('filter-data/', views.filter_data, name='filter_data'),
]