from .models import Product, UserProfile
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomLoginForm, CustomRegistrationForm
from django.db.models import Q

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
    
from django.contrib.auth.decorators import login_required



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
    top_products = Product.objects.filter(product_sold='N').order_by('-view_cnt') # 아직 팔리지 않은 물품중에 조회수 나열
    return render(request, 'carrot_app/trade.html', {'products': top_products})

# 중고거래 상세정보 화면
def trade_post(request, pk):
    post = get_object_or_404(Product, pk=pk)
    
    # 조회수 증가
    if request.user.is_authenticated: # 요청한 유저가 로그인이 되어있다면
        if request.user != post.seller: # 해당 게시글을 작성한 유저와 다르다면
            post.view_cnt += 1 # 조회수 1 증가
            post.save()
        else:
            post.view_cnt += 1
            post.save()

        try:
            user_profile = UserProfile.objects.get(user=post.seller)
        except UserProfile.DoesNotExist:
                user_profile = None

        context = {
            'post': post,
            'user_profile': user_profile,
        }

    return render(request, 'carrot_app/trade_post.html', context)

# Alert용 화면
def alert(request, alert_message):
    return render(request, 'carrot_app/alert.html', {'alert_message': alert_message})


# 상품 검색
def search(request):
    query = request.GET.get('search')
    if query:
        results = Product.objects.filter(Q(title__icontains=query) | 
                                         Q(region__icontains=query)|
                                         Q(seller__username__icontains=query))
    else:
        results = Product.objects.all()
    
    return render(request, 'carrot_app/search.html', {'posts': results})

#거래 글쓰기
@login_required
def write(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        
        if user_profile.region_certification == 'Y':
            return render(request, 'carrot_app/write.html')
        else:
            return redirect('alert', alert_message='동네인증이 필요합니다.')
    except User.DoesNotExist:
        return redirect('alert', alert_message='동네인증이 필요합니다.')
    

#거래 글 수정
def edit(request, id):
    product = get_object_or_404(Product, id=id)
    if product:
        product.description = product.description.strip()
    if request.method == "product":
        product.title = request.Post['title']
        product.price = request.Post['price']
        product.content = request.Post['content']
        product.region = request.Post['region']
        if 'images' in request.FILES:
            product.images = request.FILES['images']
        product.save()
        return redirect('trade_product', pk=id)

    return render(request, 'carrot_app/write.html', {'product': product})

