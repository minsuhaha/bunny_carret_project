from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),  # 회원가입 url
]
