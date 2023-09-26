from .models import Product
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from .forms import CustomLoginForm, CustomRegistrationForm


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
    return render(request, 'carrot_app/trade.html', {'posts': top_posts})


# 메인 화면
def main(request):
  top_views_products = Product.objects.filter(product_sold='N').order_by('-view_cnt')[:4]
  return render(request, 'carrot_app/main.html', {'products' : top_views_products})

#로그인
def user_login(request):
 # 이미 로그인한 경우
    if request.user.is_authenticated:
        return redirect('main')
    
    else:
        form = CustomLoginForm(data=request.POST or None)
        if request.method == 'POST':
           
             # 입력정보가 유효한 경우 각 필드 정보 가져옴
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
            
                user = authenticate(request, username=username, password=password)

            #로그인이 성공한 경우
            if user is not None:
                login(request, user)
                return redirect('main')  # 로그인 성공 후'main'은 리디렉션할 URL의 이름 혹은 경로
        return render(request, 'registration/login.html', {'form': form})
