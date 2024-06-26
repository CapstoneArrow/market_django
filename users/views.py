from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from .models import User
from .forms import UpdateUserForm
import random
import string
from firebase_admin import db
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer
from django.conf import settings
from django.http import JsonResponse
from django.middleware.csrf import get_token


def get_csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})


# 로그인 rest api
@api_view(['POST'])
def login_api_view(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return Response({'message': '로그인 되었습니다.'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': '이메일 또는 비밀번호가 올바르지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)


# 로그아웃 rest api
@api_view(['POST'])
def logout_api_view(request):
    logout(request)
    return Response({'message': '로그아웃 되었습니다.'}, status=status.HTTP_200_OK)


# 회원가입 rest api
@api_view(['POST'])
def signup_api_view(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        username = request.data["username"]
        password = request.data["password"]
        email = request.data["email"]

        if len(username) < 8 or len(password) < 8:
            return Response({'error': '아이디와 비밀번호는 8자 이상이어야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({'error': '이미 사용 중인 아이디입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({'error': '이미 사용 중인 이메일입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.save()
        # firebase
        ref = db.reference('users/' + user.username)
        ref.set({
            'username': user.username,
            'password': user.password,
            'email': user.email
        })
        messages.success(request, "회원가입이 완료되었습니다.")
        return Response({'message': '회원가입 되었습니다.'}, status=status.HTTP_201_CREATED)
            
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
# 아이디 찾기 rest api
@api_view(['POST'])
def find_username_api_view(request):
    # email 입력받음
    email = request.data.get("email")

    # email 전송
    try:
        user = User.objects.get(email=email)
        send_mail(
            '전통시장 아이디 찾기',
            f'가입된 아이디: {user.username}\n발신용 이메일 주소입니다.',
            settings.EMAIL_HOST_USER, # 표시되는 발송자 이메일 주소
            [email],
            fail_silently=False,
        )
        return Response({'message': '이메일로 아이디를 전송했습니다.'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': '입력하신 정보를 다시 확인해 주세요.'}, status=status.HTTP_400_BAD_REQUEST)


# 비밀번호 찾기 rest api
@api_view(['POST'])
def find_password_api_view(request):
    # username, email 입력받음
    username = request.data.get("username")
    email = request.data.get("email")

    # email 전송
    try:
        user = User.objects.get(username=username, email=email)

        # random 8자리 비밀번호 생성
        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        user.password = make_password(temp_password)

        # 파이어베이스에 발급된 임시 비밀번호로 현재 비밀번호 저장
        ref = db.reference('users/'+user.username)
        ref.update({
            'password' : temp_password
        })
        user.set_password(temp_password)
        user.save()

        send_mail(
            '전통시장 임시 비밀번호 발급',
            f'임시 비밀번호(변경 권장): {temp_password}\n발신용 이메일 주소입니다.',
            settings.EMAIL_HOST_USER,  # 표시되는 발송자 이메일 주소
            [email],
            fail_silently=False,
        )
        return Response({'message': '이메일로 임시 비밀번호를 전송했습니다.'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': '입력하신 정보를 다시 확인해 주세요.'}, status=status.HTTP_400_BAD_REQUEST)


# 회원정보 수정 rest api
@api_view(['POST', 'PUT'])
def update_profile_api_view(request):
    if request.method == 'POST':
        form = UpdateUserForm(request.data, instance=request.user)

        if form.is_valid():

            # 새로운 비밀번호와 비밀번호 확인란 채워지면 -> 새로운 비밀번호로 변경
            if form.cleaned_data['new_password'] and form.cleaned_data['confirm_new_password']:
                request.user.set_password(form.cleaned_data['new_password'])

            # 현재 username과 form의 username이 불일치하면 -> form의 username으로 변경
            if form.cleaned_data['username'] != request.user.username:
                request.user.username = form.cleaned_data['username']

            # 현재 email과 form의 email이 불일치하면 -> form의 email으로 변경
            if form.cleaned_data['email'] != request.user.email:
                request.user.email = form.cleaned_data['email']

            request.user.save()

            # firebase
            ref = db.reference('users/'+request.user.username)
            ref.update({
                'username' : request.user.username,
                'password' : request.user.password,
                'email' : request.user.email
            })

            return Response({'message': '회원정보가 변경되었습니다.'}, status=status.HTTP_200_OK)
    else:
        form = UpdateUserForm(instance=request.user)

    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'message': '회원정보가 변경되었습니다.'}, status=status.HTTP_200_OK)




###############




# 로그인
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home:home')
        else:
            messages.error(request, '이메일 또는 비밀번호가 올바르지 않습니다.')
    
    return render(request, 'users/login.html')


# 로그아웃
def logout_view(request):
    logout(request)
    return redirect("user:login")


# 회원가입
def signup_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        email = request.POST["email"]

        if len(username) < 8:
            messages.error(request, "아이디는 8자 이상이어야 합니다.")
            return redirect('user:signup')
        elif len(password) < 8:
            messages.error(request, "비밀번호는 8자 이상이어야 합니다.")
            return redirect('user:signup')
        elif User.objects.filter(username=username).exists():
            messages.error(request, "이미 사용 중인 아이디입니다.")
            return redirect('user:signup')
        elif User.objects.filter(email=email).exists():
            messages.error(request, "이미 사용 중인 이메일입니다.")
            return redirect('user:signup')
        else:
            user = User.objects.create_user(username=username, password=password, email=email)
            ref = db.reference('users/'+user.username)
            ref.set({
                'username' : user.username,
                'password' : user.password,
                'email' : user.email
            })
            messages.success(request, "회원가입이 완료되었습니다.")
            return redirect("user:login")

    return render(request, "users/signup.html")


# 아이디 찾기
def find_username_view(request):
    # email 입력받음
    if request.method == "POST":
        email = request.POST.get("email")

        # email 전송
        try:
            user = User.objects.get(email=email)
            send_mail(
                '전통시장 아이디 찾기',
                f'가입된 아이디: {user.username}\n발신용 이메일 주소입니다.',
                settings.EMAIL_HOST_USER, # 표시되는 발송자 이메일 주소
                [email],
                fail_silently=False,
            )
            messages.success(request, "등록된 이메일로 아이디를 전송했습니다.")
        
        except User.DoesNotExist:
            messages.error(request, "입력하신 정보를 다시 확인해 주세요.")
        
    return render(request, "users/find_username.html")


# 비밀번호 찾기
def find_password_view(request):
    # username, email 입력받음
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")

        # email 전송
        try:
            user = User.objects.get(username=username, email=email)

            # random 8자리 비밀번호 생성
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            user.password = make_password(temp_password)

            # 파이어베이스에 발급된 임시 비밀번호로 현재 비밀번호 저장
            ref = db.reference('users/'+user.username)
            ref.update({
                'password' : temp_password
            })
            user.set_password(temp_password)
            user.save()

            send_mail(
                '전통시장 임시 비밀번호 발급',
                f'임시 비밀번호(변경 권장): {temp_password}\n발신용 이메일 주소입니다.',
                settings.EMAIL_HOST_USER,  # 표시되는 발송자 이메일 주소
                [email],
                fail_silently=False,
            )
            messages.success(request, "등록된 이메일로 임시 비밀번호를 전송했습니다.")
        except User.DoesNotExist:
            messages.error(request, "입력하신 정보를 다시 확인해 주세요.")

    return render(request, "users/find_password.html")


# 회원정보 수정
def update_profile_view(request):
    if request.method == 'POST':
        form = UpdateUserForm(request.POST, instance=request.user)

        if form.is_valid():

            # 새로운 비밀번호와 비밀번호 확인란 채워지면 -> 새로운 비밀번호로 변경
            if form.cleaned_data['new_password'] and form.cleaned_data['confirm_new_password']:
                request.user.set_password(form.cleaned_data['new_password'])

            # 현재 username과 form의 username이 불일치하면 -> form의 username으로 변경
            if form.cleaned_data['username'] != request.user.username:
                request.user.username = form.cleaned_data['username']

            # 현재 email과 form의 email이 불일치하면 -> form의 email으로 변경
            if form.cleaned_data['email'] != request.user.email:
                request.user.email = form.cleaned_data['email']

            request.user.save()

            # firebase
            ref = db.reference('users/'+request.user.username)
            ref.update({
                'username' : request.user.username,
                'password' : request.user.password,
                'email' : request.user.email
            })
            messages.success(request, '회원정보가 변경되었습니다.')
    else:
        form = UpdateUserForm(instance=request.user)

    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{error}")

    return render(request, 'users/update_profile.html', {'form': form})