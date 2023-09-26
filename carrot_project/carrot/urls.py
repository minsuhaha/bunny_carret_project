from django.contrib import admin
from django.urls import path
from . import views

app_name = 'carret_app'

urlpatterns = [
    path('', views.main, name="main")
]
