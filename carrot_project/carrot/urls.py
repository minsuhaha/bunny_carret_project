from django.urls import path
from . import views
from django.contrib import admin
from . import views
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register, name='register'),  # 회원가입 url
    path('trade/', views.trade, name='trade'), # 중고거래화면 url
    path('', views.main, name="main"), # 메인페이지 url
    path('login/', views.user_login, name='login'), # login url
    path('logout/', auth_views.LogoutView.as_view(next_page='main'), name='logout'), # logout url
]