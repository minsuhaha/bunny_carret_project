from django.http import JsonResponse
from django.contrib import messages
from .models import Product, UserProfile, UserProfile, Category
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomLoginForm, CustomRegistrationForm, PostForm, ReviewForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q

# 메인 화면
def main(request):
  top_views_products = Product.objects.filter(product_sold='N').order_by('-view_cnt')[:4]
  return render(request, 'carrot_app/main.html', {'posts' : top_views_products})

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
    return render(request, 'carrot_app/trade.html', {'posts': top_products})

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
        
        if user_profile.region_certification == 'N':
            return render(request, 'carrot_app/write.html')
        else:
            return redirect('alert', alert_message='동네인증이 필요합니다.')
    except User.DoesNotExist:
        return redirect('alert', alert_message='동네인증이 필요합니다.')
    

#거래 글 수정
def edit(request, id):
    product = get_object_or_404(Product, id=id)
    if product:
        product.content = product.content.strip()
    if request.method == "POST":
        product.title = request.POST['title']
        product.price = request.POST['price']
        product.content = request.POST['content']
        product.region = request.POST['region']
        
        # 카테고리 저장과정
        category_id = request.POST['category']
        category = get_object_or_404(Category, id=category_id)
        product.category = category

        if 'images' in request.FILES:
            product.images = request.FILES['images']
        product.save()
        return redirect('trade_post', pk=id)

    return render(request, 'carrot_app/write.html', {'post': product})

# 포스트 업로드
@login_required
def create_post(request):

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)  # 임시 저장
            post.seller = request.user  # 작성자 정보 추가 (이 부분을 수정했습니다)
            post.save()  # 최종 저장
            return redirect('trade_post', pk=post.pk)  # 저장 후 상세 페이지로 이동
    else:
        form = PostForm()
    return render(request, 'carrot_app/trade_post.html', {'form': form})


#location Part
@login_required
def location(request):
    try:
        user_profile = UserProfile.objects.get(user_id=request.user)
        region = user_profile.region
    except UserProfile.DoesNotExist:
        region = None

    return render(request, 'carrot_app/location.html', {'region' : region})


@login_required
def set_region(request):
    if request.method == 'POST':
        region = request.POST.get('region-setting')
        
        if region:
            try:
                user_profile = UserProfile.objects.get_or_create(user=request.user)
                user_profile.region = region
                user_profile.save()
                return redirect('location')
            except Exception as e:
                return JsonResponse({ "status": "error", "message": str(e)})
        else:
            return JsonResponse({ "status": "error", "message": "지역 칸이 비어있습니다!"})
    else:
        return JsonResponse({ "status": "error", "message": "양식이 올바르지 않습니다!"}, status=405)

@login_required
def set_region_certification(request):
    if request.method == "POST":
        request.user.profile.region_certification = 'Y'
        request.user.profile.save()
        messages.success(request, "확인되었습니다!")
        return redirect('location')
    


def review (request):
    
    
    if request.method == 'POST':
        form = ReviewForm(data=request.POST or None)
        if form.is_valid():
            post = form.save()
            post.content = request.post["content"]
            post.score = request.post["score"]
            post.save()  # 최종 저장
            return redirect('trade_post', pk=post.pk)  # 저장 후 상세 페이지로 이동
    else:
        form = ReviewForm()

    return render(request, 'carrot_app/review.html', {'form': form})