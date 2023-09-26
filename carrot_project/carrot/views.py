from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from .forms import CustomLoginForm
from .models import Product
# Create your views here.

# 메인 화면
def main(request):
    top_views_posts = Product.objects.filter(product_sold='N').order_by('-view_num')[:4] 
    return render(request, 'dangun_app/main.html', {'posts': top_views_posts})

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
        return render(request, 'registraion/login.html', {'form': form})
