from django.http import JsonResponse
from django.contrib import messages
from .models import ChatRoom, Message, Product, UserProfile, UserProfile, Category
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomLoginForm, CustomRegistrationForm, PostForm
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
    except UserProfile.DoesNotExist:
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
    
# chat
def chat(request):
    return render(request, "carrot_app/chat.html")


@login_required
def chatroom_list(request):
    # 채팅방 리스트 중 하나를 클릭했을 경우
    # if request.method == "POST":
    #     chatroom_id = request.

    # chat 화면을 처음 들어왔을 경우 채팅방 리스트를 뿌려줌
    user = request.user

def get_chatrooms_context(user):
    # 현재 로그인한 사용자가 chat_host 또는 chat_guest인 ChatRoom을 검색
    chatrooms = ChatRoom.objects.filter(Q(seller=user.id) | Q(buyer=user.id))

    # 최종적으로 넘겨줄 결과 chatroom 리스트 초기화
    chatrooms_context = []

    # 각 chatroom에 대해 필요한 정보 가져옴
    for chatroom in chatrooms:
        # 채팅 상대 정보
        if chatroom.buyer == user.id:
            chat_partner = User.objects.get(id=chatroom.buyer)
        else:
            chat_partner = User.objects.get(id=chatroom.seller)

        # 상품
        product = Product.objects.get(id=chatroom.product_id)

        # 마지막 주고 받은 메시지
        last_message = Message.objects.filter(chatroom_id=chatroom.id).order_by("-sent_at").first()

        result = {
          
            'chatroom' : chatroom, # 채팅방 정보
            'chat_partner' : chat_partner, # 채팅 상대방의 정보
            'product' : product, # 상품 정보
            'message' : last_message # 마지막 메시지 정보

        }

        chatrooms_context.append(result)
    
    return chatrooms_context


@login_required
def chatroom_list(request):
    user = request.user
    
    # 참여하고 있는 채팅방 목록 및 관련 정보 불러오기
    chatrooms_context = get_chatrooms_context(user)
    
    return render(request, 'carrot_app/chat.html', {'chatrooms' : chatrooms_context})


@login_required
def chatroom(request, chatroom_id):
    user = request.user

    # 참여하고 있는 채팅방 목록 및 관련 정보 불러오기
    chatrooms_context = get_chatrooms_context(user)
    
    # 클릭한 채팅방 및 채팅 상대방에 대한 정보
    selected_chatroom = ChatRoom.objects.get(id=chatroom_id)
    if selected_chatroom.seller == user.id:
        chat_partner = User.objects.get(id=selected_chatroom.buyer)

    # 채팅 상대 정보
    chatroom = ChatRoom.objects.get(id=chatroom_id)

    if chatroom.seller == user.id:
        chat_partner = User.objects.get(id=chatroom.seller)

    else:
        chat_partner = User.objects.get(id=selected_chatroom.seller)

    # 어떤 상품에 대한 채팅방인지
    product = Product.objects.get(id=selected_chatroom.product_id)

    # 주고받은 채팅(메시지) 기록
    messages = Message.objects.filter(chatroom=chatroom_id).order_by('sent_at')

    # WebSocket 연결을 위한 주소
    ws_path = f"/ws/chat/{selected_chatroom.id}"

    # 템플릿에 전달할 데이터 정의
    context = {
        'chatrooms' : chatrooms_context,
        "selected_chatroom" : selected_chatroom,
        "product" : product,
        "chat_partner" : chat_partner,
        "messages" : messages,
        "ws_path" : ws_path,
    }

    return render(request, "carrot_app/chat.html", context)