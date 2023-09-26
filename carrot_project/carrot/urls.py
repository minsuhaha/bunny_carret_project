from django.urls import path
from . import views
from django.contrib import admin
from django.contrib.auth import views as auth_views
from .views import set_region_certification

urlpatterns = [
    path('register/', views.register, name='register'),  # 회원가입 url
    path('trade/', views.trade, name='trade'), # 중고거래화면 url
    path('trade_post/<int:pk>/', views.trade_post, name='trade_post'), # 중고거래상세화면 url
    path('', views.main, name="main"), # 메인페이지 url
    path('login/', views.user_login, name='login'), # login url
    path('logout/', auth_views.LogoutView.as_view(next_page='main'), name='logout'), # logout url
    path('search/', views.search, name='search'), # 검색 url
    path('write/', views.write, name='write'), #write url
    path('create_form/', views.create_post, name='create_form'),
    path('alert/<str:alert_message>/', views.alert, name='alert'),

    # location
    path('location/', views.location, name='location'),
    path('set_region/', views.set_region, name='set_region'),
    path('set_region_certification/', set_region_certification, name='set_region_certification'),
]