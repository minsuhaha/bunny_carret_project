from .models import Product
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import CustomRegistrationForm


# 유저 회원 가입
def register(request):
    error_message = ''
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        username = request.POST.get('username')
        if User.objects.filter(username=username).exists():
            error_message = "이미 존재하는 아이디입니다."
        elif form.is_valid():
            
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            
            # 비밀번호 일치 여부를 확인
            if password1 == password2:
                # 새로운 유저를 생성 (create_user 함수 이용)
                user = User.objects.create_user(username=username, password=password1)
                
                # 유저를 로그인 상태로 만듦
                login(request, user)
            
                return redirect('login')
            
            else:
                form.add_error('password2', 'Passwords do not match')
    else:
        form = CustomRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form, 'error_message': error_message})

# 중고거래 화면
def trade(request):
    top_posts = Product.objects.filter(product_sold='N').order_by('-view_cnt') # 아직 팔리지 않은 물품중에 조회수 나열
    return render(request, 'carret_app/trade.html', {'posts': top_posts})
from .models import Product

# Create your views here.
def main(request):
  top_views_products = Product.objects.filter(product_sold='N').order_by('-view_cnt')[:4]
  return render(request, 'carret_app/main.html', {'products' : top_views_products})