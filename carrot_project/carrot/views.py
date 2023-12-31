import json
from django.http import JsonResponse
from django.contrib import messages
from .models import ChatRoom, ChatbotMessage, ChatbotRoom, Message, Product, Review, UserProfile, UserProfile, Category
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomLoginForm, CustomRegistrationForm, PostForm, ReviewForm, UserProfileUpdateForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.urls import reverse
from django.views import View
from django.utils.decorators import method_decorator
import openai
from carrot_project.settings import secrets

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# 메인 화면
def main(request):
  top_views_products = Product.objects.filter(product_sold='N').order_by('-view_cnt')[:4]
  return render(request, 'carrot_app/main.html', {'posts' : top_views_products})

#로그인
def user_login(request):
    try:
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
                    
                    # 로그인이 성공한 경우
                    if user is not None:
                        login(request, user)
                        return redirect('main')  # 로그인 성공 후 'main'은 리디렉션할 URL의 이름 혹은 경로

        # 로그인 폼을 보여줌
        return render(request, 'registration/login.html', {'form': form})

    except UserProfile.DoesNotExist:
        # UserProfile이 없는 경우 (비회원)
        return redirect('login_alert', alert_message='로그인이 필요합니다.')
    

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

    # 페이지네이터
    page = Paginator(top_products, 8)
    page_number = request.GET.get('page')
    page_obj = page.get_page(page_number)

    if page_number=='all':
        top_products = Product.objects.filter(product_sold='N').order_by('-view_cnt')[:40]
        page = Paginator(top_products, 40)
        return render(request, 'carrot_app/trade.html', {'posts': top_products, 'page_obj': top_products})
    
    return render(request, 'carrot_app/trade.html', {'posts': top_products, 'page_obj': page_obj})

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

# Alert용 화면 - 동네 인증 알람
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
def write(request):
    if request.user.is_authenticated: # 로그인이 된 유저면
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        
            if user_profile.region_certification == 'Y':
                return render(request, 'carrot_app/write.html')
            else:
                return redirect('alert', alert_message='동네인증이 필요합니다.')
        except UserProfile.DoesNotExist:
            return redirect('alert', alert_message='동네인증이 필요합니다.')
    
    else: # 로그인이 되지 않은 유저면 
        return redirect('alert', alert_message = '로그인이 필요합니다.')
    
    

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

# 게시글 삭제 기능
@login_required
def delete_post(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    return redirect('trade')

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
        
        area = { "region" : region }

        
        area = { "region" : region }

        if region:
            try:
                user_profile = UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                user_profile = UserProfile(user=request.user)
            
            user_profile.region = region
            user_profile.save()

        return render(request, 'carrot_app/location.html', area)
    return render(request, 'carrot_app/location.html')
            
@login_required
def set_region_certification(request):
    request.user.profile.region_certification = 'Y'
    request.user.profile.save()
    # messages.success(request, "인증되었습니다")
    
    return redirect('main')
    
# chat
def get_chatrooms_context(user):
    # 현재 로그인한 사용자가 chat_host 또는 chat_guest인 ChatRoom을 검색
    chatrooms = ChatRoom.objects.filter(Q(seller_id=user.id) | Q(buyer_id=user.id))

    # 최종적으로 넘겨줄 결과 chatroom 리스트 초기화
    chatrooms_context = []

    # 각 chatroom에 대해 필요한 정보 가져옴
    for chatroom in chatrooms:
        # 채팅 상대 정보
        if chatroom.seller == user:
            chat_partner = User.objects.get(id=chatroom.buyer_id)
        else:
            chat_partner = User.objects.get(id=chatroom.seller_id)

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
    if selected_chatroom.seller == user:
        chat_partner = User.objects.get(id=selected_chatroom.buyer_id)
    else:
        chat_partner = User.objects.get(id=selected_chatroom.seller_id)

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

@login_required
def open_or_create_chatroom(request):
    if request.method == 'POST':
        # POST 요청에서 물건, 구매자 및 판매자 정보 가져오기
        data = json.loads(request.body)
        product_id = data.get('product_id')
        buyer_id = data.get('buyer_id')
        seller_id = data.get('seller_id')
        
        # buyer와 seller가 같은 경우 (채팅방 생성되지 않도록)
        if seller_id == buyer_id: # 요청하는 유저가 seller이자 buyer일 경우 (즉 채팅보기를 눌렀을때)
            existing_chatroom = ChatRoom.objects.filter(product_id = product_id).first() # 맨 처음에 채팅 한 방으로 이동시키기

            if existing_chatroom:
                # 이미 존재하는 채팅방의 URL 반환
                chatroom_url = reverse('chatroom_ws', args=[existing_chatroom.id])
                return JsonResponse({'success': True, 'chatroom_url': chatroom_url})
            
            # seller와 buyer가 같은 사람일때 해당 물건에 대한 채팅방이 아직 존재하지않는다면 alert 창 띄워주기
            return JsonResponse({'success':False})
            
        # buyer와 seller가 다른 경우
        else:
            # 이미 존재하는 채팅방인지 확인
            existing_chatroom = ChatRoom.objects.filter(
                product_id=product_id,
                seller_id=seller_id,
                buyer_id=buyer_id
            ).first()

            if existing_chatroom:
                # 이미 존재하는 채팅방의 URL 반환
                chatroom_url = reverse('chatroom_ws', args=[existing_chatroom.id])
                return JsonResponse({'success': True, 'chatroom_url': chatroom_url})
            
        
            # 존재하지 않는 경우, 새로운 채팅방 생성
            product = Product.objects.get(id=product_id)
            seller = User.objects.get(id=seller_id)
            buyer = User.objects.get(id=buyer_id)
            
            new_chatroom = ChatRoom.objects.create(product=product, seller=seller, buyer=buyer)
            chatroom_url = reverse('chatroom_ws', args=[new_chatroom.id])

            return JsonResponse({'success': True, 'chatroom_url': chatroom_url})

# 챗봇 메세지 기록 받아오는 뷰
def get_chatbot_messages(user):

    chatbot_room, created = ChatbotRoom.objects.get_or_create(user=user)  # ChatbotRoom 생성 또는 가져오기
    # 주고받은 채팅(메시지) 기록
    messages = ChatbotMessage.objects.filter(chatroom=chatbot_room).order_by('sent_at')

    return messages

# 챗봇 메세지와 채팅방 리스트 정보 가져오기
def chatbot(request):
    user = request.user

    # 참여하고 있는 채팅방 목록 및 관련 정보 불러오기
    chatrooms_context = get_chatrooms_context(user)
    chatbot_message = get_chatbot_messages(user)
    
    # 템플릿에 전달할 데이터 정의
    context = {
        'chatrooms' : chatrooms_context,
        'chatbot_message' : chatbot_message,
    }

    return render(request, "carrot_app/chatbot.html", context)

openai.api_key = secrets["openai"]

def chatbot_api(request):
    if request.method == "POST":
    
        # 사용자가 보낸 메시지를 가져옴
        user_message = request.POST.get('title')
        user = request.user  # 현재 로그인한 사용자
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_message},
                ],
            )
            # 반환된 응답에서 텍스트 추출해 변수에 저장
            bot_message = response['choices'][0]['message']['content']

            chatroom, created = ChatbotRoom.objects.get_or_create(user=user)  # 챗봇과의 대화를 위한 채팅방
            
            # 사용자 메세지 저장
            ChatbotMessage.objects.create(chatroom=chatroom, sender=user, content=user_message)
            # 챗봇 메세지 저장
            ChatbotMessage.objects.create(chatroom=chatroom, sender=user, content=bot_message, is_bot = True)
        
        except Exception as e:
            message = str(e)

        return JsonResponse({"message": bot_message})
    return render(request, 'chatbot.html')

@method_decorator(login_required, name='dispatch')
class ConfirmDealView(View):
    def post(self, request, post_id):
        product = get_object_or_404(Product, pk=post_id)
        user = request.user

        previous_url = request.META.get('HTTP_REFERER')
        url_parts = previous_url.split('/')
        original_post_id = url_parts[-2] if url_parts[-1] == '' else url_parts[-1]

        chat_room = get_object_or_404(ChatRoom, pk=original_post_id)

    
        # if chat_room.seller == user:
        #     other_user = chat_room.buyer
        # else:
        #     other_user = chat_room.seller

        if chat_room is None:
            messages.error(request, 'Chat room does not exist.')
            return redirect('trade')
        
        # buyer를 설정하고, product_sold를 Y로 설정
        product.buyer = chat_room.buyer if chat_room.seller == product.seller else chat_room.seller
        product.product_sold = 'Y'
        product.save()
        
        # 거래가 확정되면 새로고침
        return redirect('chatroom_ws', chatroom_id=chat_room.id)
    


def review(request, id, p_id):
    
    product = Product.objects.get(id=p_id)
    seller = User.objects.get(id=id)
    buyer = User.objects.get(id= request.user.id)

    if request.method == 'POST':

        form = ReviewForm(data=request.POST or None)
        if form.is_valid():
            form.save()  # 저장
            return redirect('main')  # 저장 후 메인 페이지로 이동
        else:
            return redirect('alert', alert_message='저장 왜 안됨')
    else:
        form = ReviewForm()

    return render(request, 'carrot_app/review.html', {'form': form, 'product': product, 'seller': seller, 'buyer': buyer})


# 마이페이지
def mypage(request, user_id):
    user_profile = UserProfile.objects.get(user=request.user)
    sold_products = Product.objects.filter(seller=request.user, product_sold='Y').order_by('-created_at')
    proceed_products = Product.objects.filter(seller=request.user, product_sold='N').order_by('-created_at')
    reviews = Review.objects.filter(reviewee=request.user).order_by('-created_at')
    
    context = {'user_profile' : user_profile, 'sold_products' : sold_products, 'proceed_products' : proceed_products, 'reviews' : reviews}
    return render(request, 'carrot_app/mypage2.html', context)


def edit_profile(request):
    # 현재 로그인한 사용자의 프로필 가져오기
    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            # 프로필 수정 완료 후 이동할 페이지나 메시지를 설정할 수 있습니다.
            return redirect('mypage', user_profile.id)  # 수정 후 프로필 페이지로 이동
    else:
        form = UserProfileUpdateForm(instance=user_profile)

    return render(request, 'carrot_app/profile.html')