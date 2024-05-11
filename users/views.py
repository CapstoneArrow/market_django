from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.contrib import messages
from .models import User
from .forms import UpdateUserForm
import random
import string
from firebase_admin import db


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
        user = User.objects.create_user(
            username=request.POST["username"],
            password=request.POST["password"],
            email=request.POST["email"]
            )
        ref = db.reference('users/'+user.username)
        ref.set({
            'username' : user.username,
            'password' : user.password,
            'email' : user.email
        })
        return redirect("user:login")

    return render(request, "users/signup.html")


# 아이디 찾기
def find_username_view(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
            send_mail(
                '전통시장 아이디 찾기',
                f'가입된 아이디: {user.username}',
                'email@example.com', # 표시되는 발송자 이메일 주소, 추후 수정
                [email],
                fail_silently=False,
            )
            messages.success(request, "등록된 이메일로 아이디를 전송했습니다.")
        
        except User.DoesNotExist:
            messages.error(request, "입력하신 정보를 다시 확인해 주세요.")
        
    return render(request, "users/find_username.html")


# 비밀번호 찾기
def find_password_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        try:
            user = User.objects.get(username=username, email=email)

            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            user.password = make_password(temp_password)

            ref = db.reference('users/'+user.username)
            ref.update({
                'password' : temp_password
            })
            user.set_password(temp_password)
            user.save()

            send_mail(
                '전통시장 임시 비밀번호 발급',
                f'임시 비밀번호(변경 권장): {temp_password}',
                'email@example.com',  # 표시되는 발송자 이메일 주소, 추후 수정
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
            if form.cleaned_data['new_password'] and form.cleaned_data['confirm_new_password']:
                request.user.set_password(form.cleaned_data['new_password'])

            if form.cleaned_data['username'] != request.user.username:
                request.user.username = form.cleaned_data['username']
            if form.cleaned_data['email'] != request.user.email:
                request.user.email = form.cleaned_data['email']

            request.user.save()
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