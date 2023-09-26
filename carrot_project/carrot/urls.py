from django.contrib import admin
from . import views
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    #어플리케이션 연결
    path('', views.main, name='main'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='main'), name='logout'),
]